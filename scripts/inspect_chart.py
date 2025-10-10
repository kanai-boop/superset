
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def inspect_chart():
    """
    Inspects the configuration of a chart.
    """
    client = SupersetClient()
    client.login()

    chart_id = 308

    print(f"Fetching details for chart {chart_id}...")
    try:
        chart = client.get_chart(chart_id)
        params = json.loads(chart["params"])

        print(f"--- Chart {chart_id} Params --- ")
        print(json.dumps(params, indent=2))

    except Exception as e:
        print(f"!!! Failed to fetch chart: {e}")

if __name__ == "__main__":
    inspect_chart()
