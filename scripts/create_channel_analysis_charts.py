
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from scripts.superset_tools.api_client import SupersetClient

def create_channel_analysis_charts():
    """
    Creates the charts for channel/medium/source analysis and time series.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 34  # v_ga_sessions

    # Default adhoc filter for 'Last 28 days'
    default_adhoc_filter_sql = {
        "expressionType": "SQL",
        "sqlExpression": "event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 28 DAY)",
        "clause": "WHERE",
        "subject": "event_date",
        "operator": "TEMPORAL_RANGE",
        "comparator": "Last 28 days",
        "filterOptionName": "filter_event_date_last_28_days"
    }

    # Default adhoc filter for 'No filter' (SIMPLE type)
    default_adhoc_filter_simple = {
        "expressionType": "SIMPLE",
        "subject": "event_date",
        "operator": "TEMPORAL_RANGE",
        "comparator": "No filter",
        "clause": "WHERE",
        "filterOptionName": "filter_event_date_no_filter"
    }

    # Bar Charts
    bar_charts_to_create = [
        {
            "slice_name": "チャネル",
            "groupby": ["channel_group"],
            "row_limit": 100,
            "y_axis_label": "Channel",
        },
        {
            "slice_name": "メディア TOP5",
            "groupby": ["medium"],
            "row_limit": 5,
            "y_axis_label": "Medium",
        },
        {
            "slice_name": "参照元 TOP5",
            "groupby": ["source"],
            "row_limit": 5,
            "y_axis_label": "Source",
        },
    ]

    for chart_def in bar_charts_to_create:
        params = {
            "datasource": f"{dataset_id}__table",
            "viz_type": "bar",
            "metrics": ["Users", "Sessions", "Conversions"],
            "groupby": chart_def["groupby"],
            "adhoc_filters": [default_adhoc_filter_sql, default_adhoc_filter_simple],
            "row_limit": chart_def["row_limit"],
            "rich_tooltip": True,
            "orientation": "horizontal",
            "y_axis_label": chart_def["y_axis_label"],
            "x_axis_label": "Count",
            "time_range_endpoints": ["inclusive", "exclusive"],
        }

        payload = {
            "slice_name": chart_def["slice_name"],
            "viz_type": "bar",
            "datasource_id": dataset_id,
            "datasource_type": "table",
            "params": json.dumps(params),
        }

        try:
            result = client.create_chart(payload)
            new_chart_id = result.get("id")
            print(f"Successfully created chart ''{chart_def['slice_name']}'' with ID: {new_chart_id}")
        except Exception as e:
            print(f"Error creating chart ''{chart_def['slice_name']}'': {e}")

if __name__ == "__main__":
    create_channel_analysis_charts()
