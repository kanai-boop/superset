
import json
import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from scripts.superset_tools.api_client import SupersetClient

def discover_all_datasets():
    """
    Fetches ALL datasets across all pages and prints their ID, name, and database.
    """
    client = SupersetClient()
    try:
        client.login()
        
        all_datasets = []
        page = 0
        page_size = 100
        total_datasets = 0

        while True:
            rison_q = f"(page:{page},page_size:{page_size})"
            params = {
                'q': rison_q,
                '_': int(time.time() * 1000)
            }

            response = client._request(
                "GET",
                "/api/v1/dataset/",
                params=params
            ).json()
            
            datasets_on_page = response.get('result', [])
            if not datasets_on_page:
                break
            
            all_datasets.extend(datasets_on_page)
            
            if page == 0:
                total_datasets = response.get('count', 0)

            if len(all_datasets) >= total_datasets and total_datasets > 0:
                break

            page += 1

        print("Found the following datasets:")
        print("-----------------------------------------------------------------")
        print(f"{'ID':<5} | {'Name':<50} | {'Database'}")
        print("-----------------------------------------------------------------")

        printed_ids = set()
        all_datasets.sort(key=lambda x: x.get('id', 0))

        for dataset in all_datasets:
            dataset_id = dataset.get('id')
            if dataset_id not in printed_ids:
                table_name = dataset.get('table_name')
                database_name = dataset.get('database', {}).get('database_name', 'N/A')
                print(f"{dataset_id:<5} | {table_name:<50} | {database_name}")
                printed_ids.add(dataset_id)

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    discover_all_datasets()
