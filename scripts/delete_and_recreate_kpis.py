import json
from superset_tools.api_client import SupersetClient

# This script deletes and recreates the KPI charts using the correct pattern found in chart 309.

# --- CONFIGURATION ---
CHARTS_TO_DELETE = [342, 343, 344, 345, 346, 347]

# Corrected chart definitions based on the working chart 309
CHARTS_TO_CREATE = [
    {
        "chart_name": "GA: Users",
        "viz_type": "big_number",
        "datasource_id": 34,
        "params": {
            "metric": "Users",
            "y_axis_format": ",.0f",
            "show_trend_line": True,
            "x_axis": "session_date",
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "subject": "session_date",
                    "operator": "TEMPORAL_RANGE",
                    "comparator": "Last 28 days",
                    "expressionType": "SIMPLE"
                }
            ]
        }
    },
    {
        "chart_name": "GA: New Users",
        "viz_type": "big_number",
        "datasource_id": 34,
        "params": {
            "metric": "Users",
            "y_axis_format": ",.0f",
            "show_trend_line": True,
            "x_axis": "session_date",
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "subject": "session_date",
                    "operator": "TEMPORAL_RANGE",
                    "comparator": "Last 28 days",
                    "expressionType": "SIMPLE"
                },
                {
                    "clause": "WHERE",
                    "subject": "new_vs_returning",
                    "operator": "==",
                    "comparator": "New",
                    "expressionType": "SIMPLE"
                }
            ]
        }
    },
    {
        "chart_name": "GA: Sessions",
        "viz_type": "big_number",
        "datasource_id": 34,
        "params": {
            "metric": "Sessions",
            "y_axis_format": ",.0f",
            "show_trend_line": True,
            "x_axis": "session_date",
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "subject": "session_date",
                    "operator": "TEMPORAL_RANGE",
                    "comparator": "Last 28 days",
                    "expressionType": "SIMPLE"
                }
            ]
        }
    },
    {
        "chart_name": "GA: Page Views",
        "viz_type": "big_number", # No trendline as it has no time column
        "datasource_id": 35,
        "params": {
            "metric": "Page Views",
            "y_axis_format": ",.0f"
        }
    },
    {
        "chart_name": "GA: Engagement Rate",
        "viz_type": "big_number",
        "datasource_id": 34,
        "params": {
            "metric": "Engagement Rate",
            "y_axis_format": ".2%",
            "show_trend_line": True,
            "x_axis": "session_date",
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "subject": "session_date",
                    "operator": "TEMPORAL_RANGE",
                    "comparator": "Last 28 days",
                    "expressionType": "SIMPLE"
                }
            ]
        }
    },
    {
        "chart_name": "GA: Key Events",
        "viz_type": "big_number",
        "datasource_id": 34,
        "params": {
            "metric": "Conversions",
            "y_axis_format": ",.0f",
            "show_trend_line": True,
            "x_axis": "session_date",
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "subject": "session_date",
                    "operator": "TEMPORAL_RANGE",
                    "comparator": "Last 28 days",
                    "expressionType": "SIMPLE"
                }
            ]
        }
    }
]

def delete_and_recreate_kpis():
    """
    Deletes and recreates the top-level KPI charts using the corrected pattern.
    """
    client = SupersetClient()
    client.login()

    # 1. Delete existing charts
    print(f"--- Deleting {len(CHARTS_TO_DELETE)} charts ---")
    for chart_id in CHARTS_TO_DELETE:
        try:
            client.delete_chart(chart_id)
            print(f"Successfully deleted chart {chart_id}.")
        except Exception as e:
            print(f"Could not delete chart {chart_id}. It might have been deleted already. Error: {e}")

    # 2. Recreate charts
    print(f"\n--- Recreating {len(CHARTS_TO_CREATE)} charts ---")
    for chart_def in CHARTS_TO_CREATE:
        params = chart_def['params']
        
        # Add common parameters if it's a trendline chart
        if params.get('show_trend_line'):
            common_params = {
                "compare_lag": 1,
                "comparison_type": "percentage",
                "show_delta": True,
                "show_percent": True,
                "subheader_font_size": 0.15,
            }
            params.update(common_params)

        payload = {
            "slice_name": chart_def['chart_name'],
            "viz_type": chart_def['viz_type'],
            "datasource_id": chart_def['datasource_id'],
            "datasource_type": "table",
            "params": json.dumps(params),
        }

        try:
            result = client.create_chart(payload)
            new_chart_id = result.get("id")
            print(f"Successfully created chart ''{chart_def['chart_name']}'' with ID: {new_chart_id}")
        except Exception as e:
            print(f"Error creating chart ''{chart_def['chart_name']}'' : {e}")

if __name__ == "__main__":
    delete_and_recreate_kpis()