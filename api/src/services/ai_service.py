"""AI service for analyzing meal photos using Claude Vision API."""

import base64
import io
import json
import logging
import os
from typing import Any

import anthropic
from dotenv import load_dotenv
from PIL import Image
import pillow_heif

from services.allergen_service import ALLERGEN_FOOD_MAP

# Register HEIF/HEIC support with Pillow
pillow_heif.register_heif_opener()

logger = logging.getLogger(__name__)

load_dotenv()

# Flatten ALLERGEN_FOOD_MAP to get all known foods
ALL_KNOWN_FOODS = []
for foods in ALLERGEN_FOOD_MAP.values():
    ALL_KNOWN_FOODS.extend(foods)
ALL_KNOWN_FOODS = sorted(set(ALL_KNOWN_FOODS))

# Create reverse mapping: food -> allergen
FOOD_TO_ALLERGEN = {}
for allergen, foods in ALLERGEN_FOOD_MAP.items():
    for food in foods:
        FOOD_TO_ALLERGEN[food.lower()] = allergen


def get_anthropic_client() -> anthropic.Anthropic:
    """Create Anthropic API client."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    return anthropic.Anthropic(api_key=api_key)


def get_allergens_for_food(food_name: str) -> list[str]:
    """Get list of allergens that a food contains."""
    food_lower = food_name.lower()
    allergens = []
    for allergen, foods in ALLERGEN_FOOD_MAP.items():
        if food_lower in [f.lower() for f in foods]:
            allergens.append(allergen)
    return allergens


def convert_heic_to_jpeg(image_data: bytes) -> tuple[bytes, str]:
    """
    Convert HEIC/HEIF image to JPEG.

    Returns:
        tuple of (jpeg_bytes, media_type)
    """
    img = Image.open(io.BytesIO(image_data))

    # Convert to RGB if necessary (handles RGBA, palette, etc.)
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')

    # Save as JPEG
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=90)
    output.seek(0)

    return output.read(), "image/jpeg"


def is_heic(media_type: str, image_data: bytes) -> bool:
    """Check if the image is HEIC/HEIF format."""
    if media_type in ('image/heic', 'image/heif'):
        return True
    # Check magic bytes for HEIC (ftyp followed by heic, heix, mif1, etc.)
    if len(image_data) >= 12:
        # HEIC files have 'ftyp' at offset 4
        if image_data[4:8] == b'ftyp':
            brand = image_data[8:12]
            if brand in (b'heic', b'heix', b'mif1', b'msf1', b'hevc', b'hevx'):
                return True
    return False


def analyze_meal_photo(image_data: bytes, media_type: str) -> dict[str, Any]:
    """
    Analyze a meal photo using Claude Vision API.

    Args:
        image_data: Raw image bytes
        media_type: MIME type (e.g., "image/jpeg", "image/png")

    Returns:
        dict with identified foods and their allergens
    """
    client = get_anthropic_client()

    # Convert HEIC to JPEG if needed
    if is_heic(media_type, image_data):
        logger.info("Converting HEIC image to JPEG")
        image_data, media_type = convert_heic_to_jpeg(image_data)

    # Encode image as base64
    image_base64 = base64.b64encode(image_data).decode("utf-8")

    # Build the prompt with known foods for reference
    known_foods_str = ", ".join(ALL_KNOWN_FOODS)

    prompt = f"""Analyze this photo of a baby's meal and identify all the foods present, grouped by component.

Each component represents a separate dish or side. For example:
- A side of broccoli would be one component: ["broccoli"]
- A side of rice would be another component: ["rice"]
- Yoghurt with shrimp mixed in would be one component: ["shrimp", "yoghurt"]

For each food you identify, use one of these exact names if applicable (for allergen tracking):
{known_foods_str}

If a food doesn't match any of those names exactly, use a simple, lowercase name for it.

Return your response as a JSON object with this structure:
{{
    "components": [
        {{"foods": ["food1", "food2"]}},
        {{"foods": ["food3"]}},
        ...
    ],
    "notes": "optional notes about the meal"
}}

Group foods that are mixed together or part of the same dish into a single component.
Keep separate sides as separate components.
Only include foods you can actually see in the image. Be specific (e.g., "scrambled egg" rather than just "egg" if you can tell).
Return ONLY the JSON object, no other text."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ],
    )

    # Parse the response
    response_text = message.content[0].text
    logger.info("Claude response: %s", response_text)

    # Extract JSON from response (handle markdown code blocks)
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    result = json.loads(response_text.strip())
    components = result.get("components", [])

    # Process each component
    processed_components = []
    for component in components:
        foods = component.get("foods", [])
        # Normalize food names to lowercase
        foods = [f.lower().strip() for f in foods]

        # Add allergen information for each food
        foods_with_allergens = []
        for food in foods:
            allergens = get_allergens_for_food(food)
            foods_with_allergens.append({
                "name": food,
                "allergens": allergens,
            })

        processed_components.append({
            "foods": foods_with_allergens
        })

    return {
        "components": processed_components,
        "notes": result.get("notes", ""),
    }


def get_food_suggestions() -> list[dict[str, Any]]:
    """Get all known foods with their allergen mappings for autocomplete."""
    suggestions = []
    for food in ALL_KNOWN_FOODS:
        allergens = get_allergens_for_food(food)
        suggestions.append({
            "name": food,
            "allergens": allergens,
        })
    return suggestions
