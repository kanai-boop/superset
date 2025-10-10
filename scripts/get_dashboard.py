import sys
import os
sys.path.append(os.getcwd())
import json
from scripts.superset_tools.api_client import SupersetClient

def get_dashboard():
    """
    Gets a specific dashboard by ID.
    """
    client = SupersetClient()
    client.login()

    dashboard_id = 12

    print(f"Fetching dashboard {dashboard_id}...")
    try:
        dashboard = client.get_dashboard(dashboard_id)
        print("Dashboard found:")
        print(json.dumps(dashboard, indent=2))

    except Exception as e:
        print(f"!!! Failed to fetch dashboard {dashboard_id}: {e}")

if __name__ == "__main__":
    get_dashboard()