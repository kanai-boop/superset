
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def create_heatmap_chart():
    """
    Creates a Day of Week / Hour Heatmap chart using dataset 32.
    """
    client = SupersetClient()
    client.login()

    datasource_id = 32
    slice_name = "Day of Week / Hour Heatmap"

    # Using the working parameters from the user's test chart (303) as a template
    # and adapting for the new dataset and desired axes.
    params = {
        "datasource": f"{datasource_id}__table",
        "viz_type": "heatmap_v2",
        "x_axis": "hour",  # From the new dataset
        "groupby": "segments_day_of_week", # From the new dataset
        "metric": "clicks", # Default metric, can be changed
        "adhoc_filters": [
            {
                "clause": "WHERE",
                "subject": "date", # Use the 'date' column from the new dataset
                "operator": "TEMPORAL_RANGE",
                "comparator": "No filter",
                "expressionType": "SIMPLE"
            }
        ],
        "row_limit": 10000,
        "normalize_across": "heatmap",
        "legend_type": "continuous",
        "linear_color_scheme": "superset_seq_1",
        "border_color": {"r": 0, "g": 0, "b": 0, "a": 1},
        "xscale_interval": -1,
        "yscale_interval": -1,
        "left_margin": "auto",
        "bottom_margin": "auto",
        "value_bounds": [None, None],
        "y_axis_format": "SMART_NUMBER",
        "x_axis_time_format": "smart_date",
        "show_legend": True,
        "show_percentage": True,
        "extra_form_data": {},
    }

    payload = {
        "slice_name": slice_name,
        "viz_type": params["viz_type"],
        "datasource_id": datasource_id,
        "datasource_type": "table",
        "params": json.dumps(params),
    }

    print(f"Creating Heatmap chart for {slice_name}...")
    try:
        resp = client._request("POST", "/api/v1/chart/", json=payload)
        chart_id = resp.json()["id"]
        print(f"Successfully created chart '{slice_name}' with ID: {chart_id}")
        return chart_id
    except Exception as e:
        print(f"!!! Failed to create chart '{slice_name}': {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    create_heatmap_chart()
