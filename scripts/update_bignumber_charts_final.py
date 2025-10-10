
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def update_bignumber_charts_final(chart_ids):
    """
    Updates a list of Big Number charts with the correct parameters for
    time comparison, based on learned correct values.
    """
    client = SupersetClient()
    client.login()

    print(f"Updating {len(chart_ids)} Big Number charts with correct parameters...")

    for chart_id in chart_ids:
        try:
            print(f"-- Updating chart {chart_id} --")
            chart_data = client.get_chart(chart_id)
            params = json.loads(chart_data.get("params", "{}"))

            # Add/overwrite with the correct, learned parameters
            params["compare_lag"] = 1
            params["subheader_font_size"] = 0.15
            params["comparison_type"] = "percentage" # To show Δ%

            payload = {"params": json.dumps(params)}
            client.update_chart(chart_id, payload)
            print(f"Successfully updated chart {chart_id}.")

        except Exception as e:
            print(f"!!! Failed to update chart {chart_id}: {e}", file=sys.stderr)

if __name__ == "__main__":
    # The other 5 charts, excluding the one manually fixed (276)
    chart_ids_to_update = [277, 278, 279, 280, 281]
    update_bignumber_charts_final(chart_ids_to_update)

