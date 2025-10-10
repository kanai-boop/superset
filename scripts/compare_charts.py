
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def compare_charts():
    """
    Compares the configuration of two charts.
    """
    client = SupersetClient()
    client.login()

    chart_id_a = 303 # User's chart
    chart_id_b = 304 # My chart

    print(f"Fetching details for chart {chart_id_a} and {chart_id_b}...")
    try:
        chart_a = client.get_chart(chart_id_a)
        chart_b = client.get_chart(chart_id_b)

        params_a = json.loads(chart_a["params"])
        params_b = json.loads(chart_b["params"])

        print("--- Chart 303 (User's) --- ")
        print(json.dumps(params_a, indent=2))

        print("\n--- Chart 304 (Mine) --- ")
        print(json.dumps(params_b, indent=2))
        
        # A simple way to find differences
        print("\n--- Differences (User -> Mine) ---")
        for key in params_a:
            if key not in params_b:
                print(f"Missing key in Chart 304: {key}")
            elif params_a[key] != params_b[key]:
                print(f"Difference in '{key}':")
                print(f"  303: {params_a[key]}")
                print(f"  304: {params_b[key]}")
        
        for key in params_b:
            if key not in params_a:
                print(f"Extra key in Chart 304: {key}")

    except Exception as e:
        print(f"!!! Failed to fetch or compare charts: {e}")

if __name__ == "__main__":
    compare_charts()
