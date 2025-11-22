
import json
import copy
from superset_tools.api_client import SupersetClient

def fix_kpi_charts():
    """
    Fixes the newly created KPI charts that are showing errors.
    - Corrects the time column for charts on dataset 34.
    - Updates the Engagement Rate chart to use the new metric.
    - Changes the Page Views chart to a non-trendline version.
    """
    client = SupersetClient()
    client.login()

    # --- Charts to fix on Dataset 34 ---
    charts_ds34 = {
        342: {"metric": "Users"}, # GA: Users
        343: {"metric": "Users"}, # GA: New Users
        344: {"metric": "Sessions"}, # GA: Sessions
        346: {"metric": "Engagement Rate"}, # GA: Engagement Rate
        347: {"metric": "Conversions"} # GA: Key Events
    }

    print("--- Fixing charts on Dataset 34 ---")
    for chart_id, updates in charts_ds34.items():
        try:
            print(f"Fixing chart {chart_id}...")
            chart_info = client.get_chart(chart_id)
            params = json.loads(chart_info['result']['params'])

            # Correction: Use the correct time column
            params['time_column_sqla'] = 'session_date'
            # Correction: Update metric for engagement rate chart
            if chart_id == 346:
                params['metric'] = updates['metric']

            payload = {"params": json.dumps(params)}
            client.update_chart(chart_id, payload)
            print(f"Successfully updated chart {chart_id}.")
        except Exception as e:
            print(f"Error updating chart {chart_id}: {e}")

    # --- Chart to fix on Dataset 35 ---
    chart_id_ds35 = 345 # GA: Page Views
    print("\n--- Fixing chart on Dataset 35 ---")
    try:
        print(f"Fixing chart {chart_id_ds35}...")
        chart_info = client.get_chart(chart_id_ds35)
        params = json.loads(chart_info['result']['params'])

        # Correction: Change viz_type to big_number and remove trendline params
        params['viz_type'] = 'big_number'
        params.pop('time_column_sqla', None)
        params.pop('time_grain_sqla', None)
        params.pop('compare_lag', None)
        params.pop('comparison_type', None)
        params.pop('show_trend_line', None)
        params.pop('show_delta', None)
        params.pop('show_percent', None)

        payload = {
            "viz_type": "big_number",
            "params": json.dumps(params)
        }
        client.update_chart(chart_id_ds35, payload)
        print(f"Successfully updated chart {chart_id_ds35}.")
    except Exception as e:
        print(f"Error updating chart {chart_id_ds35}: {e}")

if __name__ == "__main__":
    fix_kpi_charts()
