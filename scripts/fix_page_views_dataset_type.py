
import json
from superset_tools.api_client import SupersetClient

def fix_page_views_dataset_type():
    """
    Finds the event_date column in dataset 35 and explicitly sets its type to DATE and is_dttm to true.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 35
    print(f"Fixing column type for 'event_date' in dataset {dataset_id}...")

    try:
        dataset_info = client.get_dataset(dataset_id, q={'columns': ['columns']})
        existing_columns = dataset_info['result']['columns']

        found_and_updated = False
        # Create a new list of columns, keeping only the required fields
        cleaned_columns = []
        for col in existing_columns:
            # We must remove all read-only fields for the PUT request
            cleaned_col = {
                "column_name": col["column_name"],
                "verbose_name": col.get("verbose_name"),
                "description": col.get("description"),
                "is_dttm": col.get("is_dttm", False),
                "is_active": col.get("is_active", True),
                "filterable": col.get("filterable", True),
                "groupby": col.get("groupby", True),
                "python_date_format": col.get("python_date_format"),
                "type": col.get("type")
            }
            # Find and update the target column
            if cleaned_col["column_name"] == "event_date":
                print("Found event_date column. Setting is_dttm=true and type=DATE.")
                cleaned_col["is_dttm"] = True
                cleaned_col["type"] = "DATE"
                found_and_updated = True
            
            cleaned_columns.append(cleaned_col)

        if not found_and_updated:
            print("Error: Could not find 'event_date' column in the dataset.")
            return

        # For column updates, we must send the full list back.
        payload = {"columns": cleaned_columns}

        client.update_dataset(dataset_id, payload)
        print("Successfully updated the column type for 'event_date'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fix_page_views_dataset_type()
