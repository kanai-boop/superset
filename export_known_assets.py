
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from scripts.superset_tools.api_client import SupersetClient

CHART_IDS = [276, 282, 397, 398, 399, 400]
DATASET_ID = 34

def export_known_assets():
    """
    Fetches the full configuration for a known list of charts and datasets.
    """
    client = SupersetClient()
    output = {
        "datasets": [],
        "charts": []
    }

    try:
        client.login()

        # Fetch dataset details
        print(f"Fetching dataset {DATASET_ID}...")
        q = {"columns": ["columns", "metrics"]}
        dataset_data = client.get_dataset(DATASET_ID, q=q)
        output["datasets"].append(dataset_data)

        # Fetch chart details
        for chart_id in CHART_IDS:
            print(f"Fetching chart {chart_id}...")
            chart_data = client.get_chart(chart_id)
            output["charts"].append(chart_data)
        
        # Print the consolidated JSON output
        print("\n--- Consolidated JSON Output ---")
        print(json.dumps(output, indent=2))

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    export_known_assets()

