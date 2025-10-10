
import sys
import json
from scripts.superset_tools.api_client import SupersetClient

def find_big_number_charts(chart_ids):
    """
    Finds and prints details of charts with viz_type 'big_number' from a given list of IDs.
    """
    client = SupersetClient()
    client.login()

    print("Searching for Big Number charts...")
    found_charts = []
    for chart_id in chart_ids:
        try:
            chart_data = client.get_chart(chart_id)
            if chart_data.get("viz_type") == "big_number":
                found_charts.append({
                    "id": chart_data["id"],
                    "slice_name": chart_data["slice_name"]
                })
        except Exception as e:
            print(f"Could not fetch chart {chart_id}: {e}", file=sys.stderr)
    
    if not found_charts:
        print("No Big Number charts found in the specified range.")
    else:
        print("Found the following Big Number charts:")
        print(json.dumps(found_charts, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # As per the session summary, the latest charts are in this range.
    chart_id_range = range(276, 286)
    find_big_number_charts(chart_id_range)

