
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def clean_list_of_dicts(list_of_dicts, keys_to_remove):
    """Removes specified keys from a list of dictionaries."""
    if not list_of_dicts:
        return []
    cleaned_list = []
    for item in list_of_dicts:
        # Keep the id for existing items, but remove other read-only fields
        # This is a guess based on the "already exist" error
        cleaned_item = {k: v for k, v in item.items() if k not in keys_to_remove}
        if 'id' in item:
            cleaned_item['id'] = item['id'] # Try re-adding the id
        cleaned_list.append(cleaned_item)
    return cleaned_list

def add_hour_column():
    """
    Adds a calculated column 'segments_hour' to dataset 31.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 31
    column_name = "segments_hour"
    sql_expression = "EXTRACT(HOUR FROM segments_date)"

    print(f"Fetching dataset {dataset_id}...")
    try:
        dataset = client.get_dataset(dataset_id)
        
        if any(c['column_name'] == column_name for c in dataset["columns"]):
            print(f"Column '{column_name}' already exists in dataset {dataset_id}.")
            return

        new_column = {
            "column_name": column_name,
            "verbose_name": "Hour of Day",
            "description": "Calculated column for the hour of the day from segments_date.",
            "expression": sql_expression,
            "filterable": True,
            "groupby": True,
            "is_dttm": False,
            "type": "INT",
            "is_active": True,
        }

        # Let's try a new cleaning strategy. The API might need the ID to identify existing columns.
        # The previous MARSHMALLOW error was about unknown fields. Let's try removing them but keeping the ID.
        
        final_columns = []
        for col in dataset["columns"]:
            final_columns.append({
                "id": col["id"],
                "column_name": col["column_name"],
                "verbose_name": col.get("verbose_name"),
                "description": col.get("description"),
                "expression": col.get("expression"),
                "filterable": col.get("filterable"),
                "groupby": col.get("groupby"),
                "is_dttm": col.get("is_dttm"),
                "type": col.get("type"),
                "is_active": col.get("is_active"),
                "python_date_format": col.get("python_date_format"),
            })
        final_columns.append(new_column) # Add the new column without an ID

        # The same for metrics
        final_metrics = []
        for met in dataset["metrics"]:
             final_metrics.append({
                "id": met["id"],
                "metric_name": met["metric_name"],
                "verbose_name": met.get("verbose_name"),
                "description": met.get("description"),
                "expression": met.get("expression"),
                "metric_type": met.get("metric_type"),
                "d3format": met.get("d3format"),
                "currency": met.get("currency"),
                "warning_text": met.get("warning_text"),
            })

        update_payload = {
            "columns": final_columns,
            "metrics": final_metrics,
            "owners": [owner["id"] for owner in dataset.get("owners", [])],
            "schema": dataset.get("schema"),
            "table_name": dataset.get("table_name"),
        }

        print(f"Adding calculated column '{column_name}' to dataset {dataset_id}...")
        client.update_dataset(dataset_id, update_payload)
        print("Successfully added column.")

        print("Refreshing dataset schema...")
        client.refresh_dataset(dataset_id)
        print("Successfully refreshed dataset.")

    except Exception as e:
        print(f"!!! Failed to add column: {e}")

if __name__ == "__main__":
    add_hour_column()
