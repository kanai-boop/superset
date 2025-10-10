import json
import sys
import uuid
from scripts.superset_tools.api_client import SupersetClient

def add_calculated_column(dataset_id: int, column_name: str, expression: str, column_type: str, verbose_name: str = None):
    """
    Adds a new calculated column to a dataset.
    """
    client = SupersetClient()
    client.login()

    print(f"Fetching dataset {dataset_id}...")
    dataset = client.get_dataset(dataset_id)

    # Extract existing columns and filter out read-only/problematic fields
    columns = []
    for col in dataset.get("columns", []):
        filtered_col = {
            k: v for k, v in col.items() if k not in ["created_on", "changed_on", "type_generic", "id", "uuid"]
        }
        # Ensure 'extra' is a string if it exists and is a dict
        if "extra" in filtered_col and isinstance(filtered_col["extra"], dict):
            filtered_col["extra"] = json.dumps(filtered_col["extra"])
        columns.append(filtered_col)

    # Check if column already exists
    if any(c.get("column_name") == column_name for c in columns):
        print(f"Column '{column_name}' already exists in dataset {dataset_id}. Skipping addition.")
        return

    # Define the new calculated column
    new_column = {
        "column_name": column_name,
        "verbose_name": verbose_name if verbose_name else column_name,
        "expression": expression,
        "type": column_type,
        "filterable": True,
        "groupby": True,
        "is_active": True,
        "is_dttm": False, # Not a datetime column itself, but derived from one
        "extra": "{}", # Ensure extra is an empty string dict
        "uuid": str(uuid.uuid4()),
    }
    columns.append(new_column)
    print(f"Defined new calculated column: '{column_name}'.")

    # Construct the payload for update_dataset with only allowed fields
    update_payload = {
        "database_id": dataset["database"]["id"],
        "owners": [owner["id"] for owner in dataset["owners"]],
        "schema": dataset.get("schema"),
        "table_name": dataset.get("table_name"),
        "main_dttm_col": dataset.get("main_dttm_col"),
        "columns": columns, # Send the updated columns list
    }

    print(f"Updating dataset {dataset_id} with new column '{column_name}'...")
    client.update_dataset(dataset_id, update_payload)
    print(f"Successfully updated dataset {dataset_id}.")

    print(f"Refreshing dataset {dataset_id} metadata...")
    client.refresh_dataset(dataset_id)
    print(f"Successfully refreshed dataset {dataset_id}.")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python -m scripts.add_calculated_column <dataset_id> <column_name> <expression> <column_type>")
        sys.exit(1)

    try:
        dataset_id_arg = int(sys.argv[1])
        column_name_arg = sys.argv[2]
        expression_arg = sys.argv[3]
        column_type_arg = sys.argv[4]
        add_calculated_column(dataset_id_arg, column_name_arg, expression_arg, column_type_arg)
    except ValueError:
        print("Error: Dataset ID must be an integer.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)