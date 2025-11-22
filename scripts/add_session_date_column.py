
import json
from superset_tools.api_client import SupersetClient

def add_session_date_column():
    """
    Adds a calculated column 'session_date' to dataset 34.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 34

    try:
        # Fetch existing columns to avoid duplication
        dataset_info = client.get_dataset(dataset_id, q={'columns': ['columns']})
        existing_columns = dataset_info['result']['columns']

        if any(c['column_name'] == 'session_date' for c in existing_columns):
            print("Calculated column 'session_date' already exists. Skipping.")
            return

        print("Adding calculated column 'session_date'...")

        # The knowledge base says to send ONLY the new column definition when adding a calculated column.
        new_column = {
            "column_name": "session_date",
            "verbose_name": "Session Date",
            "is_dttm": True,
            "type": "DATE",
            "expression": "CAST(session_start_timestamp AS DATE)"
        }

        # The payload should only contain the new column to be added.
        payload = {"columns": [new_column]}

        client.update_dataset(dataset_id, payload)
        print("Successfully added calculated column 'session_date'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    add_session_date_column()
