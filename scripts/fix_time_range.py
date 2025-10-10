
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def fix_time_range():
    """
    Updates the time_range for the WoW chart to be an enclosed range.
    """
    client = SupersetClient()
    client.login()

    chart_id_to_fix = 306

    print(f"Updating time_range for chart {chart_id_to_fix}...")
    try:
        chart = client.get_chart(chart_id_to_fix)
        params = json.loads(chart["params"])

        # The error indicates an enclosed time range is needed.
        # Let's change "Last 90 days" to a format with a start and end.
        new_time_range = "Last 90 days : today"
        print(f"Changing time_range to: '{new_time_range}'")
        params["time_range"] = new_time_range

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
    fix_time_range()
