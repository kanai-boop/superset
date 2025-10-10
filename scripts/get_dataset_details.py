
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def get_dataset_details(dataset_id: int):
    """
    Fetches and prints the details of a specific dataset.
    """
    client = SupersetClient()
    client.login()
    dataset_data = client.get_dataset(dataset_id)
    print(json.dumps(dataset_data, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_dataset_details.py <dataset_id>")
        sys.exit(1)
    
    try:
        dataset_id_arg = int(sys.argv[1])
        get_dataset_details(dataset_id_arg)
    except ValueError:
        print("Error: Dataset ID must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
