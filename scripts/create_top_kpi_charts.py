
import json
from superset_tools.api_client import SupersetClient

def create_top_kpi_charts():
    """
    Creates the main KPI charts for the top of the GA Dashboard.
    """
    client = SupersetClient()
    client.login()

    charts_to_create = [
        {
            "chart_name": "GA: Users",
            "viz_type": "big_number_with_trendline",
            "datasource_id": 34, # v_ga_sessions
            "params": {
                "metric": "Users",
                "time_column_sqla": "session_date",
                "y_axis_format": ",.0f"
            }
        },
        {
            "chart_name": "GA: New Users",
            "viz_type": "big_number_with_trendline",
            "datasource_id": 34, # v_ga_sessions
            "params": {
                "metric": "Users",
                "time_column_sqla": "session_date",
                "adhoc_filters": [
                    {
                        "clause": "WHERE",
                        "subject": "new_vs_returning",
                        "operator": "==",
                        "comparator": "New",
                        "expressionType": "SIMPLE"
                    }
                ],
                "y_axis_format": ",.0f"
            }
        },
        {
            "chart_name": "GA: Sessions",
            "viz_type": "big_number_with_trendline",
            "datasource_id": 34, # v_ga_sessions
            "params": {
                "metric": "Sessions",
                "time_column_sqla": "session_date",
                "y_axis_format": ",.0f"
            }
        },
        {
            "chart_name": "GA: Page Views",
            "viz_type": "big_number_with_trendline",
            "datasource_id": 35, # v_ga_page_views
            "params": {
                "metric": "Page Views",
                "time_column_sqla": "event_date", # Assuming event_date in v_ga_page_views
                "y_axis_format": ",.0f"
            }
        },
        {
            "chart_name": "GA: Engagement Rate",
            "viz_type": "big_number_with_trendline",
            "datasource_id": 34, # v_ga_sessions
            "params": {
                "metric": "engagement_rate",
                "time_column_sqla": "session_date",
                "y_axis_format": ".2%"
            }
        },
        {
            "chart_name": "GA: Key Events",
            "viz_type": "big_number_with_trendline",
            "datasource_id": 34, # v_ga_sessions
            "params": {
                "metric": "Conversions",
                "time_column_sqla": "session_date",
                "y_axis_format": ",.0f"
            }
        }
    ]

    print(f"Creating {len(charts_to_create)} KPI charts...")

    for chart_def in charts_to_create:
        # Common parameters for all KPI charts
        common_params = {
            "datasource": f"{chart_def['datasource_id']}__table",
            "viz_type": chart_def['viz_type'],
            "time_range_endpoints": ["inclusive", "exclusive"],
            "time_grain_sqla": "P1D",
            "compare_lag": 1,
            "comparison_type": "percentage",
            "show_trend_line": True,
            "start_y_axis_at_zero": True,
            "show_delta": True,
            "show_percent": True,
            "subheader_font_size": 0.15,
        }
        
        # Merge specific params with common params
        params = {**chart_def['params'], **common_params}

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
            print(f"Error creating chart ''{chart_def['chart_name']}'': {e}")

if __name__ == "__main__":
    create_top_kpi_charts()
