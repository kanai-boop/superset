
import json
import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from scripts.superset_tools.api_client import SupersetClient

def discover_all_charts():
    """
    Fetches ALL charts across all pages and prints their ID, name, and datasource.
    """
    client = SupersetClient()
    try:
        client.login()
        
        all_charts = []
        page = 0
        page_size = 100
        total_charts = 0

        while True:
            # Per documentation, construct the RISON string for the 'q' parameter
            rison_q = f"(page:{page},page_size:{page_size})"
            
            # Add a cache-busting parameter
            params = {
                'q': rison_q,
                '_': int(time.time() * 1000) # current time in milliseconds
            }

            response = client._request(
                "GET",
                "/api/v1/chart/",
                params=params
            ).json()
            
            charts_on_page = response.get('result', [])
            if not charts_on_page:
                break
            
            all_charts.extend(charts_on_page)
            
            # Use the 'count' from the first response to know the total
            if page == 0:
                total_charts = response.get('count', 0)

            # Exit if we've fetched all or more than the total count
            if len(all_charts) >= total_charts and total_charts > 0:
                break

            page += 1

        print("Found the following charts:")
        print("-----------------------------------------------------------------")
        print(f"{'ID':<5} | {'Name':<50} | {'Datasource'}")
        print("-----------------------------------------------------------------")

        # Use a set to keep track of printed IDs to avoid duplicates
        printed_ids = set()
        all_charts.sort(key=lambda x: x.get('id', 0))

        for chart in all_charts:
            chart_id = chart.get('id')
            if chart_id not in printed_ids:
                chart_name = chart.get('slice_name')
                datasource_name = chart.get('datasource_name_text', 'N/A')
                print(f"{chart_id:<5} | {chart_name:<50} | {datasource_name}")
                printed_ids.add(chart_id)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    discover_all_charts()
