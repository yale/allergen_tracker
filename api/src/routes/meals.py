"""Meal logging endpoints."""

import logging
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from services.ai_service import analyze_meal_photo, get_food_suggestions
from services.meal_service import submit_meal

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/meals", tags=["meals"])


class FoodItem(BaseModel):
    name: str
    allergens: list[str]


class MealComponent(BaseModel):
    foods: list[FoodItem]


class AnalyzeResponse(BaseModel):
    components: list[MealComponent]
    notes: str


class SubmitRequest(BaseModel):
    components: list[list[str]]  # List of components, each component is a list of food names


class MealEntry(BaseModel):
    entry_id: str
    foods: list[str]


class SubmitResponse(BaseModel):
    status: str
    entries: list[MealEntry]  # Multiple entries, one per component
    timestamp: str


class FoodSuggestion(BaseModel):
    name: str
    allergens: list[str]


class SuggestionsResponse(BaseModel):
    suggestions: list[FoodSuggestion]


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_meal(image: UploadFile = File(...)):
    """
    Analyze a meal photo and identify foods.

    Returns identified foods with their allergen information.
    """
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read image data
    image_data = await image.read()

    # Limit file size (10MB)
    if len(image_data) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    try:
        result = analyze_meal_photo(image_data, image.content_type)
        components = []
        for component_data in result["components"]:
            foods = [FoodItem(**f) for f in component_data["foods"]]
            components.append(MealComponent(foods=foods))

        return AnalyzeResponse(
            components=components,
            notes=result.get("notes", ""),
        )
    except Exception as e:
        logger.error("Error analyzing meal photo: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=SubmitResponse)
async def submit_meal_entry(request: SubmitRequest):
    """
    Submit confirmed foods to Huckleberry.

    Creates multiple solid food entries in Firestore, one per component.
    """
    if not request.components:
        raise HTTPException(status_code=400, detail="No components provided")

    # Validate that each component has at least one food
    for i, component in enumerate(request.components):
        if not component:
            raise HTTPException(status_code=400, detail=f"Component {i} has no foods")

    try:
        result = submit_meal(request.components)
        return SubmitResponse(**result)
    except RuntimeError as e:
        logger.error("Error submitting meal: %s", e)
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error("Error submitting meal: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions():
    """
    Get all known foods for autocomplete.

    Returns foods with their allergen mappings.
    """
    suggestions = get_food_suggestions()
    return SuggestionsResponse(
        suggestions=[FoodSuggestion(**s) for s in suggestions]
    )
