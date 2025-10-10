
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def fix_dual_axis_chart(chart_id: int):
    """
    Configures a mixed time-series chart to use dual axes with proper formatting.
    """
    client = SupersetClient()
    client.login()

    print(f"Fetching chart {chart_id}...")
    chart_data = client.get_chart(chart_id)
    
    params_str = chart_data.get("params")
    if not params_str:
        print("Error: Chart has no 'params' field.")
        return

    params = json.loads(params_str)

    print("Reconfiguring for dual-axis display...")

    # Assign metrics to left and right axes
    params['metrics'] = ['cost']
    params['secondary_metrics'] = ['roas']
    if 'metrics_b' in params:
        del params['metrics_b'] # Remove legacy key

    # Enable dual-axis mode
    params['use_y_axis_2'] = True

    # Set d3 formats for each axis
    params['y_axis_format'] = '~s'  # SI format for cost (e.g., 100K, 1M)
    params['y_axis_2_format'] = '.2%' # Percentage format for roas

    payload = {"params": json.dumps(params)}

    print("Updating chart...")
    client.update_chart(chart_id, payload)

    print(f"Chart {chart_id} has been updated for dual-axis display.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.fix_dual_axis_chart <chart_id>")
        sys.exit(1)

    try:
        chart_id_arg = int(sys.argv[1])
        fix_dual_axis_chart(chart_id_arg)
    except ValueError:
        print("Error: Chart ID must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

