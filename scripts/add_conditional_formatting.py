
import sys
import os
sys.path.append(os.getcwd())

import json
from scripts.superset_tools.api_client import SupersetClient

def add_conditional_formatting():
    """
    Adds conditional formatting to the WoW Performance Snapshot chart.
    """
    client = SupersetClient()
    client.login()

    chart_id_to_fix = 306

    print(f"Adding conditional formatting to chart {chart_id_to_fix}...")
    try:
        chart = client.get_chart(chart_id_to_fix)
        params = json.loads(chart["params"])

        # Define the WoW columns. The naming convention is 'metric_name WoW'.
        wow_columns = [
            "cost WoW", 
            "conversions WoW", 
            "cpa WoW", 
            "roas WoW"
        ]
        
        formatting_rules = []
        for col in wow_columns:
            # Rule for positive change (Green)
            formatting_rules.append({
                "colorScheme": "d3.interpolateGnBu", # A green-ish scheme
                "column": col,
                "operator": ">",
                "targetValue": 0
            })
            # Rule for negative change (Red)
            formatting_rules.append({
                "colorScheme": "d3.interpolateYlOrRd", # A red-ish scheme
                "column": col,
                "operator": "<",
                "targetValue": 0
            })

        params["conditional_formatting"] = formatting_rules

        # Prepare the payload
        update_payload = {
            "params": json.dumps(params),
        }

        # Update the chart
        client.update_chart(chart_id_to_fix, update_payload)
        print(f"Successfully added conditional formatting to chart {chart_id_to_fix}.")

    except Exception as e:
        print(f"!!! Failed to update chart: {e}")

if __name__ == "__main__":
    add_conditional_formatting()
