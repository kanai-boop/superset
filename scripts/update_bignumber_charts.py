
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def update_bignumber_charts(chart_ids):
    """
    Updates a list of Big Number charts to show comparison to the previous period.
    """
    client = SupersetClient()
    client.login()

    print(f"Updating {len(chart_ids)} Big Number charts...")

    for chart_id in chart_ids:
        try:
            print(f"-- Updating chart {chart_id} --")
            chart_data = client.get_chart(chart_id)
            params = json.loads(chart_data.get("params", "{}"))

            # Add parameters for time comparison
            # NOTE: 'previous period' is a guess based on common Superset values.
            params["time_compare"] = "previous period"
            params["show_delta"] = True
            params["show_percent"] = True
            params["subheader_font_size"] = 12 # Make the subheader text smaller

            payload = {"params": json.dumps(params)}
            client.update_chart(chart_id, payload)
            print(f"Successfully updated chart {chart_id}.")

        except Exception as e:
            print(f"!!! Failed to update chart {chart_id}: {e}", file=sys.stderr)

if __name__ == "__main__":
    bignumber_chart_ids = [276, 277, 278, 279, 280, 281]
    update_bignumber_charts(bignumber_chart_ids)

