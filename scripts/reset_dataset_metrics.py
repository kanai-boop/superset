
import json
from superset_tools.api_client import SupersetClient

def reset_dataset_metrics(dataset_id: int):
    """
    Deletes all metrics from a given dataset by overwriting with an empty list.
    """
    client = SupersetClient()
    client.login()

    # Define a payload with an empty list for metrics
    payload = {"metrics": []}

    print(f"Attempting to delete all metrics from dataset {dataset_id}...")

    try:
        client.update_dataset(dataset_id, payload)
        print(f"Successfully deleted all metrics from dataset {dataset_id}.")
    except Exception as e:
        print(f"Error deleting metrics from dataset {dataset_id}: {e}")


if __name__ == "__main__":
    DATASET_ID = 34
    reset_dataset_metrics(DATASET_ID)
