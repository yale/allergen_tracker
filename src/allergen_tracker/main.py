from huckleberry_api import HuckleberryAPI
from dotenv import load_dotenv
from datetime import datetime
import os


def get_api_client():
    """Create and authenticate Huckleberry API client."""
    load_dotenv()

    api = HuckleberryAPI(
        email=os.getenv("HUCKLEBERRY_EMAIL"),
        password=os.getenv("HUCKLEBERRY_PASSWORD")
    )
    api.authenticate()

    return api


def fetch_all_feed_intervals(client, child_uid):
    """
    Fetch all feed intervals including both regular and batched entries.

    Returns:
        list: List of tuples (entry_id, entry_data)
    """
    feed_ref = client.collection("feed").document(child_uid)
    intervals_ref = feed_ref.collection("intervals")

    print("Fetching regular intervals...")
    regular_intervals = []
    for doc in intervals_ref.order_by("start", direction="DESCENDING").stream():
        data = doc.to_dict()
        if not data.get("multi"):  # Not a multi-entry batch document
            regular_intervals.append((doc.id, data))

    print(f"Regular intervals: {len(regular_intervals)}")

    # Fetch multi-entry batch documents (Huckleberry batches older data)
    print("Fetching multi-entry batch documents...")
    multi_docs = list(intervals_ref.where("multi", "==", True).stream())
    print(f"Multi-entry batch documents: {len(multi_docs)}")

    # Extract individual entries from batch documents
    batched_entries = []
    for doc in multi_docs:
        doc_data = doc.to_dict()
        if not doc_data or not isinstance(doc_data.get("data"), dict):
            continue

        # Each batch document has a "data" field with nested entries
        for entry_id, entry in doc_data["data"].items():
            if isinstance(entry, dict) and "start" in entry:
                batched_entries.append((f"{doc.id}:{entry_id}", entry))

    print(f"Entries from batched documents: {len(batched_entries)}")

    # Combine all entries
    all_entries = regular_intervals + batched_entries
    print(f"\nTotal feed entries: {len(all_entries)}")

    return all_entries


def extract_solid_food_entries(all_entries):
    """
    Filter feed entries to extract only solid food entries.

    Returns:
        list: List of tuples (entry_id, entry_data) sorted by timestamp (newest first)
    """
    # Filter for solids and sort by timestamp
    solid_entries = [(entry_id, data) for entry_id, data in all_entries if data.get("mode") == "solids"]
    solid_entries.sort(key=lambda x: x[1].get("start", 0), reverse=True)

    return solid_entries


def print_solid_food_entry(entry_num, doc_id, entry):
    """Print a single solid food entry in a formatted way."""
    # Parse timestamp
    timestamp = entry.get("start", 0)
    dt = datetime.fromtimestamp(timestamp)

    # Get foods
    foods = entry.get("foods", {})
    food_names = [food_data.get("created_name", "Unknown") for food_data in foods.values()]

    # Get notes and reactions
    notes = entry.get("notes", "")
    reactions = entry.get("reactions", {})

    print(f"\n#{entry_num} - {dt.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Document ID: {doc_id}")
    print(f"\nFoods ({len(food_names)}):")
    for food_name in sorted(food_names):
        print(f"  • {food_name}")

    if notes:
        print(f"\nNotes: {notes}")

    if reactions:
        print(f"\nReactions: {reactions}")

    # Show detailed food data
    print(f"\nDetailed food data:")
    for food_id, food_data in foods.items():
        source = food_data.get("source", "unknown")
        name = food_data.get("created_name", "Unknown")
        print(f"  • {name} ({source})")

    print("\n" + "=" * 80)


def main():
    """Main function to fetch and display solid food entries."""
    try:
        # Initialize API and get child info
        api = get_api_client()
        children = api.get_children()
        child_uid = children[0]["uid"]

        print(f"Children: {children}")
        print()

        # Get Firestore client
        client = api._get_firestore_client()
        print(f"Firestore Client: {client}")
        print()

        # Fetch all feed intervals
        print("=== FETCHING ALL FEED INTERVALS ===\n")
        all_entries = fetch_all_feed_intervals(client, child_uid)

        # Extract solid food entries
        solid_entries = extract_solid_food_entries(all_entries)

        # Print summary
        print(f"\n{'=' * 80}")
        print(f"SOLID FOOD ENTRIES: {len(solid_entries)} total")
        print("=" * 80)

        # Print all solid food entries
        for i, (doc_id, entry) in enumerate(solid_entries, 1):
            print_solid_food_entry(i, doc_id, entry)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
