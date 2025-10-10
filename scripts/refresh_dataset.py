
import sys
from pathlib import Path

# Add script's parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.superset_tools.api_client import SupersetClient

def refresh_dataset_metadata(dataset_id: int):
    """
    Refreshes the metadata for a given dataset.
    """
    print(f"Attempting to refresh metadata for dataset {dataset_id}...")
    client = SupersetClient()
    
    try:
        client.login()
        print("Successfully logged in to Superset API.")

        result = client.refresh_dataset(dataset_id)
        print(f"Successfully triggered refresh for dataset {dataset_id}.")
        print("API Response:", result)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    DATASET_ID = 31
    refresh_dataset_metadata(DATASET_ID)
