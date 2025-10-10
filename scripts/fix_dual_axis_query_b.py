
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def fix_dual_axis_query_b(chart_id: int):
    """
    Fixes a mixed time-series chart by using 'metrics_b' instead of 'secondary_metrics'
    for the second query, which is required by some versions of Superset.
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

    print("Reverting to 'metrics_b' for Query B...")

    # Ensure metrics for Query A are set
    params['metrics'] = ['cost']
    
    # Use 'metrics_b' for Query B
    params['metrics_b'] = ['roas']
    if 'secondary_metrics' in params:
        del params['secondary_metrics']

    # Keep the other dual-axis settings
    params['use_y_axis_2'] = True
    params['y_axis_format'] = '~s'
    params['y_axis_2_format'] = '.2%'

    payload = {"params": json.dumps(params)}

    print("Updating chart...")
    client.update_chart(chart_id, payload)

    print(f"Chart {chart_id} has been updated to use 'metrics_b'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.fix_dual_axis_query_b <chart_id>")
        sys.exit(1)

    try:
        chart_id_arg = int(sys.argv[1])
        fix_dual_axis_query_b(chart_id_arg)
    except ValueError:
        print("Error: Chart ID must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

