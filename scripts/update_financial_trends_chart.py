
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def update_financial_trends_chart(chart_id: int):
    """
    Updates the Financial Trends chart to include Revenue.
    """
    client = SupersetClient()
    client.login()

    print(f"Fetching chart {chart_id}...")
    chart_data = client.get_chart(chart_id)
    params = json.loads(chart_data.get("params", "{}"))

    print("Updating Financial Trends chart to include Revenue...")

    # --- Query and Metric assignment ---
    params['metrics'] = ['cost', 'revenue']
    params['metrics_b'] = ['roas']

    # --- Axis Assignment (CRITICAL) ---
    params['yAxisIndex'] = 0
    params['yAxisIndexB'] = 1

    # --- Chart Type Assignment ---
    params['seriesType'] = 'line'
    params['seriesTypeB'] = 'line'

    # --- Axis Formatting ---
    params['y_axis_format'] = '~s'
    params['y_axis_format_secondary'] = '.2%'

    # Ensure dual-axis is enabled
    params['use_y_axis_2'] = True

    payload = {"params": json.dumps(params)}

    print("Updating chart...")
    client.update_chart(chart_id, payload)

    print(f"Chart {chart_id} (Financial Trends) updated successfully to include Revenue.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.update_financial_trends_chart <chart_id>")
        sys.argv = [sys.argv[0], "282"] # Default to chart 282

    try:
        chart_id_arg = int(sys.argv[1])
        update_financial_trends_chart(chart_id_arg)
    except ValueError:
        print("Error: Chart ID must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
