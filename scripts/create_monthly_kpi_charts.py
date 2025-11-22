
import json
from superset_tools.api_client import SupersetClient

def create_monthly_kpi_charts():
    """
    Creates KPI charts for 'This Month', 'Last Month', and '2 Months Ago' for various metrics.
    """
    client = SupersetClient()
    client.login()

    metrics_config = [
        {
            "name": "Users",
            "metric_key": "Users",
            "datasource_id": 34,
            "y_axis_format": ",0f",
            "adhoc_filters": []
        },
        {
            "name": "New Users",
            "metric_key": "Users",
            "datasource_id": 34,
            "y_axis_format": ",0f",
            "adhoc_filters": [
                {
                    "clause": "WHERE",
                    "subject": "new_vs_returning",
                    "operator": "==",
                    "comparator": "New",
                    "expressionType": "SIMPLE"
                }
            ]
        },
        {
            "name": "Sessions",
            "metric_key": "Sessions",
            "datasource_id": 34,
            "y_axis_format": ",0f",
            "adhoc_filters": []
        },
        {
            "name": "Page Views",
            "metric_key": "Page Views",
            "datasource_id": 35,
            "y_axis_format": ",0f",
            "adhoc_filters": []
        },
        {
            "name": "Engagement Rate",
            "metric_key": "Engagement Rate",
            "datasource_id": 34,
            "y_axis_format": ".2%",
            "adhoc_filters": []
        },
        {
            "name": "Avg Engagement Time",
            "metric_key": "Avg Engagement Time (sec)",
            "datasource_id": 34,
            "y_axis_format": ",1fS",
            "adhoc_filters": []
        },
        {
            "name": "CVR",
            "metric_key": "Conversion Rate",
            "datasource_id": 34,
            "y_axis_format": ".2%",
            "adhoc_filters": []
        },
        {
            "name": "Key Events",
            "metric_key": "Conversions",
            "datasource_id": 34,
            "y_axis_format": ",0f",
            "adhoc_filters": []
        }
    ]

    time_ranges = {
        "今月合計": "Current Month",
        "先月合計": "Last Month",
        "2ヶ月前合計": "Previous Month" # This will be the month before "Last Month"
    }

    charts_to_create = []

    for metric_conf in metrics_config:
        for period_name, time_range_comp in time_ranges.items():
            chart_name = f"GA: {metric_conf['name']} ({period_name})"
            
            # Base adhoc filters for the metric
            base_adhoc_filters = list(metric_conf['adhoc_filters'])

            # Add temporal filter
            temporal_filter = {
                "clause": "WHERE",
                "subject": "event_date" if metric_conf["datasource_id"] == 35 else "session_date",
                "operator": "TEMPORAL_RANGE",
                "comparator": time_range_comp,
                "expressionType": "SIMPLE"
            }
            adhoc_filters = base_adhoc_filters + [temporal_filter]

            chart_def = {
                "chart_name": chart_name,
                "viz_type": "big_number", # No trendline for monthly totals
                "datasource_id": metric_conf['datasource_id'],
                "params": {
                    "metric": metric_conf['metric_key'],
                    "y_axis_format": metric_conf['y_axis_format'],
                    "adhoc_filters": adhoc_filters,
                    "time_range_endpoints": ["inclusive", "exclusive"], # Always include for consistency
                }
            }
            charts_to_create.append(chart_def)

    print(f"Creating {len(charts_to_create)} monthly KPI charts...")

    for chart_def in charts_to_create:
        params = chart_def['params']
        params["datasource"] = f"{chart_def['datasource_id']}__table"

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
    create_monthly_kpi_charts()
