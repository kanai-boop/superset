
import sys
from pathlib import Path

# Add script's parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from scripts.superset_tools.api_client import SupersetClient

def set_main_dttm_col(dataset_id: int, col_name: str):
    """
    Sets the main_dttm_col for a given dataset.
    """
    print(f"Attempting to set 'main_dttm_col' to '{col_name}' for dataset {dataset_id}...")
    client = SupersetClient()
    
    try:
        client.login()
        print("Successfully logged in to Superset API.")

        payload = {"main_dttm_col": col_name}
        
        # We need to get the full dataset config first, as the API overwrites everything
        dataset = client.get_dataset(dataset_id)
        
        # Create the payload for update
        update_payload = {
            "database_id": dataset["database"]["id"],
            "owners": [owner["id"] for owner in dataset["owners"]],
            "schema": dataset.get("schema"),
            "table_name": dataset.get("table_name"),
            "main_dttm_col": col_name,
        }

        result = client.update_dataset(dataset_id, update_payload)
        print(f"Successfully updated dataset {dataset_id}.")
        print("API Response:", result)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    DATASET_ID = 31
    COLUMN_NAME = "segments_date"
    set_main_dttm_col(DATASET_ID, COLUMN_NAME)
