

import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def check_dataset_details():
    """
    Checks the columns and metrics of a specified dataset.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 33

    print(f"Fetching details for dataset {dataset_id}...")
    try:
        dataset = client.get_dataset(dataset_id)
        
        print(f"--- Dataset {dataset_id} ---")
        print(f"Table Name: {dataset.get('table_name')}")
        print(f"SQL: {dataset.get('sql')}")

        print("\nColumns:")
        columns = dataset.get("columns", [])
        for col in columns:
            is_calc = "(calculated)" if col.get('expression') else "(physical)"
            print(f"- {col['column_name']} {is_calc} (type: {col['type']})")

        print("\nMetrics:")
        metrics = dataset.get("metrics", [])
        if not metrics:
            print("No metrics defined for this dataset.")
        else:
            for met in metrics:
                print(f"- {met['metric_name']}: {met['expression']}")

    except Exception as e:
        print(f"!!! Failed to fetch dataset details: {e}")

if __name__ == "__main__":
    check_dataset_details()

