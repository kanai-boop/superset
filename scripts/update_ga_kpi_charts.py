import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def update_ga_kpi_charts_for_trendline():
    """
    Updates GA KPI charts to the correct viz_type and adds a time column
    to enable trendline display.
    """
    client = SupersetClient()
    client.login()

    chart_ids_to_update = [308, 309]

    for chart_id in chart_ids_to_update:
        print(f"Updating chart {chart_id} for trendline display...")
        try:
            chart = client.get_chart(chart_id)
            params = json.loads(chart["params"])
            
            # 1. Change viz_type to 'big_number' which supports trendlines
            params["viz_type"] = "big_number"

            # 2. Specify the time column for the trendline
            params["x_axis"] = "event_date_parsed"

            # 3. Ensure other trendline/comparison params are still there
            params["show_trend_line"] = True
            params["compare_lag"] = 1
            params["comparison_type"] = "percentage"
            params["show_delta"] = True
            params["show_percent"] = True
            params["subheader_font_size"] = 0.15

            # Prepare the payload - must update top-level viz_type as well
            update_payload = {
                "viz_type": params["viz_type"],
                "params": json.dumps(params),
            }

            # Update the chart
            client.update_chart(chart_id, update_payload)
            print(f"Successfully updated chart {chart_id}.")

        except Exception as e:
            print(f"!!! Failed to update chart {chart_id}: {e}", file=sys.stderr)

if __name__ == "__main__":
    update_ga_kpi_charts_for_trendline()