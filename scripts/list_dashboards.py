
import sys
import os
sys.path.append(os.getcwd())

from scripts.superset_tools.api_client import SupersetClient

def list_dashboards():
    """
    Lists all available dashboards.
    """
    client = SupersetClient()
    client.login()

    print("Fetching dashboards...")
    try:
        # There is no direct "list" endpoint in the client, so we use a GET on the base resource
        resp = client._request("GET", "/api/v1/dashboard/")
        dashboards = resp.json()["result"]
        
        if not dashboards:
            print("No dashboards found.")
            return

        print("Available dashboards:")
        for dash in dashboards:
            print(f"- ID: {dash['id']}, Title: {dash['dashboard_title']}")

    except Exception as e:
        print(f"!!! Failed to fetch dashboards: {e}")

if __name__ == "__main__":
    list_dashboards()
