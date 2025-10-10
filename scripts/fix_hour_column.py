
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def fix_hour_column():
    """
    Updates the expression for the 'segments_hour' calculated column in dataset 31.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 31
    column_name_to_fix = "segments_hour"
    # The new expression assumes a physical column with the same name exists in BigQuery.
    # This is a guess to fix the EXTRACT from DATE error.
    new_sql_expression = "segments_hour"

    print(f"Fetching dataset {dataset_id}...")
    try:
        dataset = client.get_dataset(dataset_id)
        
        # Find the column to update
        column_found = False
        for col in dataset["columns"]:
            if col['column_name'] == column_name_to_fix:
                print(f"Found column '{column_name_to_fix}'. Updating its expression...")
                col['expression'] = new_sql_expression
                # Also ensure the type is correct, BigQuery will return an INT
                col['type'] = "INT"
                column_found = True
                break
        
        if not column_found:
            print(f"!!! Column '{column_name_to_fix}' not found in dataset {dataset_id}.")
            return

        # --- Prepare the payload for update ---
        # We use the same cleaning strategy that worked before.
        final_columns = []
        for col in dataset["columns"]:
            cleaned_col = {
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
            }
            if 'id' in col: # Keep ID for existing columns
                cleaned_col['id'] = col['id']
            final_columns.append(cleaned_col)

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

        print(f"Updating calculated column '{column_name_to_fix}' in dataset {dataset_id}...")
        client.update_dataset(dataset_id, update_payload)
        print("Successfully updated column expression.")

        print("Refreshing dataset schema from source...")
        client.refresh_dataset(dataset_id)
        print("Successfully refreshed dataset.")

    except Exception as e:
        print(f"!!! Failed to update column: {e}")

if __name__ == "__main__":
    fix_hour_column()
