import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def sort_heatmap_xaxis():
    """
    Updates the heatmap chart to ensure the X-axis (hour) is sorted correctly.
    This is done by adding x-axis sorting parameters.
    """
    client = SupersetClient()
    client.login()

    chart_id_to_fix = 304

    print(f"Updating chart {chart_id_to_fix} to fix X-axis sorting...")
    try:
        chart = client.get_chart(chart_id_to_fix)
        params = json.loads(chart["params"])

        # Add sorting parameters. This is a guess based on Superset conventions.
        # We want to sort the x-axis by its own value, ascending.
        # In some viz types, this is controlled by `x_axis_sort` and `x_axis_sort_asc`
        # or similar. Let's try a common pattern.
        params["sort_x_axis"] = "alpha_asc" # Sort by the axis label, ascending

        print("Adding 'sort_x_axis': 'alpha_asc' to params...")

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
    sort_heatmap_xaxis()