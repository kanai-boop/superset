
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from scripts.superset_tools.api_client import SupersetClient

def add_channel_group_column(dataset_id: int):
    """
    Adds a calculated column 'channel_group' to the specified dataset.
    """
    client = SupersetClient()
    client.login()

    # The expression for the calculated column
    channel_group_expression = """
CASE
  WHEN medium = 'organic' THEN 'Organic Search'
  WHEN medium = 'cpc' THEN 'Paid Search'
  WHEN medium = 'referral' THEN 'Referral'
  WHEN medium = '(none)' AND source = '(direct)' THEN 'Direct'
  WHEN medium LIKE '%social%' THEN 'Social'
  ELSE 'Unassigned'
END
"""

    # Define the new column
    new_column_payload = {
        "column_name": "channel_group",
        "verbose_name": "Channel Group",
        "expression": channel_group_expression,
        "type": "STRING",
        "filterable": True,
        "groupby": True,
        "is_active": True,
        "description": "Derived channel grouping based on medium and source.",
    }

    # The API expects a list of columns to update/add. For adding a new column,
    # we send only the new column definition.
    update_payload = {"columns": [new_column_payload]}

    print(f"Attempting to add 'channel_group' calculated column to dataset {dataset_id}...")
    try:
        # Fetch existing columns to avoid overwriting them if the API requires it,
        # though the guide suggests sending only the new column for addition.
        # For safety, let's try to get existing columns and append, then send the full list.
        # However, the guide explicitly says '新しい計算列を追加する場合は、ペイロードに新しい列の定義のみを含めることで成功した。'
        # So, we will follow that guidance and send only the new column.
        result = client.update_dataset(dataset_id, update_payload)
        print(f"Successfully added 'channel_group' to dataset {dataset_id}: {result}")
    except Exception as e:
        print(f"Error adding 'channel_group' to dataset {dataset_id}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    add_channel_group_column(34) # Dataset ID for v_ga_sessions
