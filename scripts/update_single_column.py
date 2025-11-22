
import json
from superset_tools.api_client import SupersetClient

def update_single_column():
    """
    Updates a single column in a dataset. This is a targeted approach.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 35
    column_id_to_update = 1126 # The ID of the 'event_date' column

    print(f"Updating column {column_id_to_update} in dataset {dataset_id}...")

    try:
        # To modify an existing column, we send ONLY that column's definition,
        # including its ID and the fields to be changed.
        payload = {
            "columns": [
                {
                    "id": column_id_to_update,
                    "column_name": "event_date", # Must include column_name
                    "is_dttm": True,
                    "type": "DATE"
                }
            ]
        }

        client.update_dataset(dataset_id, payload)
        print("Successfully updated the column type for 'event_date'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_single_column()
