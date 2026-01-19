"""Huckleberry API client for fetching solid food entries."""

from huckleberry_api import HuckleberryAPI
from dotenv import load_dotenv
import os


def get_api_client() -> HuckleberryAPI:
    """Create and authenticate Huckleberry API client."""
    load_dotenv()

    api = HuckleberryAPI(
        email=os.getenv("HUCKLEBERRY_EMAIL"),
        password=os.getenv("HUCKLEBERRY_PASSWORD")
    )
    api.authenticate()

    return api


def fetch_all_feed_intervals(client, child_uid: str) -> list[tuple[str, dict]]:
    """
    Fetch all feed intervals including both regular and batched entries.

    Returns:
        list: List of tuples (entry_id, entry_data)
    """
    feed_ref = client.collection("feed").document(child_uid)
    intervals_ref = feed_ref.collection("intervals")

    # Fetch regular intervals
    regular_intervals = []
    for doc in intervals_ref.order_by("start", direction="DESCENDING").stream():
        data = doc.to_dict()
        if not data.get("multi"):
            regular_intervals.append((doc.id, data))

    # Fetch multi-entry batch documents (Huckleberry batches older data)
    multi_docs = list(intervals_ref.where("multi", "==", True).stream())

    # Extract individual entries from batch documents
    batched_entries = []
    for doc in multi_docs:
        doc_data = doc.to_dict()
        if not doc_data or not isinstance(doc_data.get("data"), dict):
            continue

        for entry_id, entry in doc_data["data"].items():
            if isinstance(entry, dict) and "start" in entry:
                batched_entries.append((f"{doc.id}:{entry_id}", entry))

    return regular_intervals + batched_entries


def extract_solid_food_entries(all_entries: list[tuple[str, dict]]) -> list[dict]:
    """
    Filter feed entries to extract only solid food entries.

    Returns:
        list: List of entry_data dicts sorted by timestamp (newest first)
    """
    solid_entries = [data for entry_id, data in all_entries if data.get("mode") == "solids"]
    solid_entries.sort(key=lambda x: x.get("start", 0), reverse=True)
    return solid_entries


def fetch_solid_food_entries() -> list[dict]:
    """Fetch all solid food entries from Huckleberry."""
    api = get_api_client()
    children = api.get_children()
    child_uid = children[0]["uid"]

    client = api._get_firestore_client()
    all_entries = fetch_all_feed_intervals(client, child_uid)
    return extract_solid_food_entries(all_entries)
