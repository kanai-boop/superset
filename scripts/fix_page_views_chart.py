
import json
from superset_tools.api_client import SupersetClient

def fix_page_views_chart():
    """
    Updates the Page Views chart (ID 345) to be a trendline chart now that the dataset is fixed.
    """
    client = SupersetClient()
    client.login()

    chart_id = 345
    print(f"Updating chart {chart_id} to a trendline KPI...")

    try:
        # Get the current params
        chart_info = client.get_chart(chart_id)
        params = json.loads(chart_info['result']['params'])

        # Update params to the correct trendline pattern
        params['viz_type'] = 'big_number'
        params['show_trend_line'] = True
        params['x_axis'] = 'event_date'
        params['adhoc_filters'] = [
            {
                "clause": "WHERE",
                "subject": "event_date",
                "operator": "TEMPORAL_RANGE",
                "comparator": "Last 28 days",
                "expressionType": "SIMPLE"
            }
        ]
        params['compare_lag'] = 1
        params['comparison_type'] = 'percentage'
        params['show_delta'] = True
        params['show_percent'] = True
        params['subheader_font_size'] = 0.15

        payload = {
            "params": json.dumps(params),
            "viz_type": "big_number" # Also update the top-level viz_type
        }

        client.update_chart(chart_id, payload)
        print(f"Successfully updated chart {chart_id}.")

    except Exception as e:
        print(f"An error occurred while updating chart {chart_id}: {e}")

if __name__ == "__main__":
    fix_page_views_chart()
