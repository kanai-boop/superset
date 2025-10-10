import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def rename_wow_columns():
    """
    Renames the ugly WoW column headers in the table chart using their full internal names.
    """
    client = SupersetClient()
    client.login()

    chart_id_to_fix = 306

    print(f"Updating column labels for chart {chart_id_to_fix} using full internal names...")
    try:
        chart = client.get_chart(chart_id_to_fix)
        params = json.loads(chart["params"])

        # Use the full, ugly internal names as keys, based on the user's screenshot.
        # The pattern seems to be percentage__<metric>__<metric>__1 week ago
        # Note: The exact name might vary slightly, but this pattern is the most likely.
        # Let's try to construct them based on the metrics used in the chart.
        metrics = params.get("metrics", [])
        original_wow_columns = {}
        for metric in metrics:
            # Construct the ugly name. The duplication of the metric name is strange but observed.
            ugly_name = f"percentage__{metric}__{metric}__1 week ago"
            clean_label = f"{metric.replace('_', ' ').title()} WoW Δ%"
            original_wow_columns[ugly_name] = clean_label

        # Initialize column_config if it doesn't exist
        if "column_config" not in params:
            params["column_config"] = {}

        print("Applying new labels:")
        for original_name, new_label in original_wow_columns.items():
            print(f"  - '{original_name}' -> '{new_label}'")
            params["column_config"][original_name] = {"label": new_label}

        # Prepare the payload
        update_payload = {
            "params": json.dumps(params),
        }

        # Update the chart
        client.update_chart(chart_id_to_fix, update_payload)
        print(f"\nSuccessfully updated column labels for chart {chart_id_to_fix}.")

    except Exception as e:
        print(f"!!! Failed to update chart: {e}")

if __name__ == "__main__":
    rename_wow_columns()