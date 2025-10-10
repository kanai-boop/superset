import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def check_columns():
    """
    Checks the columns of a specified dataset, including their expressions.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 32

    print(f"Fetching details for dataset {dataset_id}...")
    try:
        dataset = client.get_dataset(dataset_id)
        columns = dataset.get("columns", [])
        
        print(f"--- Dataset {dataset_id} ---")
        print(f"Table Name: {dataset.get('table_name')}")
        print(f"SQL: {dataset.get('sql')}")
        print("\nColumns:")
        for col in columns:
            is_calc = "(calculated)" if col.get('expression') else "(physical)"
            print(f"- {col['column_name']} {is_calc}\n    type: {col['type']}")

    except Exception as e:
        print(f"!!! Failed to fetch dataset details: {e}")

if __name__ == "__main__":
    check_columns()