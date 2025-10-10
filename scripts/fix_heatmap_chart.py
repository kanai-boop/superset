
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def fix_heatmap_chart():
    """
    Updates chart 304 to match the working configuration of chart 303.
    """
    client = SupersetClient()
    client.login()

    chart_id_to_fix = 304
    working_chart_id = 303

    print(f"Fixing chart {chart_id_to_fix} based on chart {working_chart_id}...")
    try:
        # Get the working chart's params to use as a template
        working_chart = client.get_chart(working_chart_id)
        working_params = json.loads(working_chart["params"])

        # --- Create the new, corrected params ---
        # The goal is a Day of Week vs Hour heatmap, so we adapt the working config.
        new_params = working_params.copy()
        
        # Key changes based on the comparison and the desired output
        new_params["viz_type"] = "heatmap_v2" # The main fix
        new_params["x_axis"] = "segments_hour"   # What we want on the x-axis
        new_params["groupby"] = "segments_day_of_week" # What we want on the y-axis (in v2)
        new_params["metric"] = "clicks" # heatmap_v2 seems to take a single metric

        # Remove params from the old viz_type that are not in the new one
        # and add defaults from the working one if they are missing.
        params_to_remove = [
            "y_axis", "metrics", "x_axis_label", "y_axis_label", "legendType",
            "legendOrientation", "xAxisLabelInterval", "rich_tooltip", "showTooltipTotal",
            "tooltipTimeFormat", "truncateXAxis", "y_axis_bounds", "logAxis",
            "query_mode", "granularity_sqla"
        ]
        for p in params_to_remove:
            new_params.pop(p, None)

        # Ensure all necessary keys from the working chart are present
        for key, value in working_params.items():
            if key not in new_params:
                new_params[key] = value

        # Get the chart we need to fix
        chart_to_fix = client.get_chart(chart_id_to_fix)

        # Prepare the payload
        update_payload = {
            "slice_name": chart_to_fix["slice_name"], # Keep the original name
            "viz_type": new_params["viz_type"],
            "params": json.dumps(new_params),
        }

        print("\n--- New Parameters for Chart 304 ---")
        print(json.dumps(new_params, indent=2))

        # Update the chart
        client.update_chart(chart_id_to_fix, update_payload)
        print(f"\nSuccessfully updated chart {chart_id_to_fix}.")

    except Exception as e:
        print(f"!!! Failed to fix chart: {e}")

if __name__ == "__main__":
    fix_heatmap_chart()
