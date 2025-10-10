
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def add_metrics_to_ga_dataset():
    """
    Adds necessary metrics (SUM(sessions), SUM(users)) to dataset 33.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 33

    print(f"Fetching dataset {dataset_id}...")
    try:
        dataset = client.get_dataset(dataset_id)

        # --- Define the new metrics ---
        new_metrics_definitions = {
            "sessions": "SUM(sessions)",
            "users": "SUM(users)",
        }
        
        existing_metric_names = {m['metric_name'] for m in dataset["metrics"]}
        
        metrics_to_add = []
        for name, expression in new_metrics_definitions.items():
            if name not in existing_metric_names:
                print(f"Metric '{name}' does not exist. Preparing to add it.")
                metrics_to_add.append({
                    "metric_name": name,
                    "expression": expression,
                    "verbose_name": name.replace("_", " ").title(),
                    "metric_type": "aggregation",
                    "d3format": ",.0f",
                })
        
        if not metrics_to_add:
            print("All necessary metrics already exist.")
            # Even if they exist, we should still run the update to be safe
            # return

        dataset["metrics"].extend(metrics_to_add)

        # --- Prepare the payload for update ---
        # Use the cleaning strategy that worked before
        final_columns = []
        for col in dataset["columns"]:
            cleaned_col = {
                "column_name": col["column_name"],
                "type": col.get("type"),
            }
            if 'id' in col: cleaned_col['id'] = col['id']
            final_columns.append(cleaned_col)

        final_metrics = []
        for met in dataset["metrics"]:
            cleaned_met = {
                "metric_name": met["metric_name"],
                "expression": met.get("expression"),
                "verbose_name": met.get("verbose_name"),
                "metric_type": met.get("metric_type"),
                "d3format": met.get("d3format"),
            }
            if 'id' in met: cleaned_met['id'] = met['id']
            final_metrics.append(cleaned_met)

        update_payload = {
            "columns": final_columns,
            "metrics": final_metrics,
            "owners": [owner["id"] for owner in dataset.get("owners", [])],
        }

        print(f"Adding/updating metrics for dataset {dataset_id}...")
        client.update_dataset(dataset_id, update_payload)
        print("Successfully added/updated metrics.")

    except Exception as e:
        print(f"!!! Failed to add metrics: {e}")

if __name__ == "__main__":
    add_metrics_to_ga_dataset()
