
import json
from superset_tools.api_client import SupersetClient

def create_trend_charts():
    """
    Creates a series of Mixed Time-series charts for the GA Dashboard.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 34

    # Define the charts to create
    # For dual-axis charts, specify metrics for left (metrics) and right (metrics_b) axes.
    charts_to_create = [
        {
            "chart_name": "GA: Users & Sessions (Daily)",
            "viz_type": "mixed_timeseries",
            "metrics": ["Users", "Sessions"],
            "metrics_b": [], # Single axis
        },
        {
            "chart_name": "GA: Conversions & Revenue (Daily)",
            "viz_type": "mixed_timeseries",
            "metrics": ["Conversions"], # Left axis
            "metrics_b": ["Revenue"], # Right axis
        },
        {
            "chart_name": "GA: Conv. Rate & AOV (Daily)",
            "viz_type": "mixed_timeseries",
            "metrics": ["Conversion Rate"], # Left axis
            "metrics_b": ["AOV"], # Right axis
        },
    ]

    print(f"Creating {len(charts_to_create)} trend charts for dataset {dataset_id}...")

    for chart_def in charts_to_create:
        is_dual_axis = bool(chart_def["metrics_b"])

        params = {
            "datasource": f"{dataset_id}__table",
            "viz_type": chart_def["viz_type"],
            "x_axis": "session_start_timestamp",
            "time_grain_sqla": "P1D",
            "metrics": chart_def["metrics"],
            "seriesType": "line",
            "opacity": 0.2,
            "markerEnabled": True,
            "markerSize": 6,
        }

        if is_dual_axis:
            params.update({
                "metrics_b": chart_def["metrics_b"],
                "yAxisIndex": 0,
                "yAxisIndexB": 1,
                "seriesTypeB": "line",
            })

        payload = {
            "slice_name": chart_def["chart_name"],
            "viz_type": chart_def["viz_type"],
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": json.dumps(params),
        }

        try:
            result = client.create_chart(payload)
            new_chart_id = result.get("id")
            print(f"Successfully created chart ''{chart_def['chart_name']}'' with ID: {new_chart_id}")
        except Exception as e:
            print(f"Error creating chart ''{chart_def['chart_name']}'': {e}")

if __name__ == "__main__":
    create_trend_charts()
