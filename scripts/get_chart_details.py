
import json
import sys
from scripts.superset_tools.api_client import SupersetClient

def get_chart_details(chart_id: int):
    """
    Fetches and prints the details of a specific chart.
    """
    client = SupersetClient()
    client.login()
    chart_data = client.get_chart(chart_id)
    print(json.dumps(chart_data, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_chart_details.py <chart_id>")
        sys.exit(1)
    
    try:
        chart_id_arg = int(sys.argv[1])
        get_chart_details(chart_id_arg)
    except ValueError:
        print("Error: Chart ID must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
