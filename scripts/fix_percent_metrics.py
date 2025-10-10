
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def fix_percent_metrics():
    """
    Removes items from the percent_metrics list for the WoW chart.
    """
    client = SupersetClient()
    client.login()

    chart_id_to_fix = 306

    print(f"Updating percent_metrics for chart {chart_id_to_fix}...")
    try:
        chart = client.get_chart(chart_id_to_fix)
        params = json.loads(chart["params"])

        if "percent_metrics" in params and params["percent_metrics"]:
            print(f"Original percent_metrics: {params['percent_metrics']}")
            params["percent_metrics"] = []
            print("percent_metrics have been cleared.")
        else:
            print("No percent_metrics to clear.")
            return

        # Prepare the payload
        update_payload = {
            "params": json.dumps(params),
        }

        # Update the chart
        client.update_chart(chart_id_to_fix, update_payload)
        print(f"Successfully updated chart {chart_id_to_fix}.")

    except Exception as e:
        print(f"!!! Failed to update chart: {e}")

if __name__ == "__main__":
    fix_percent_metrics()
