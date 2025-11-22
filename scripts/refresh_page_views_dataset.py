
from superset_tools.api_client import SupersetClient

def refresh_page_views_dataset():
    """
    Refreshes the v_ga_page_views dataset (ID 35) to sync columns from source.
    """
    client = SupersetClient()
    client.login()

    dataset_id = 35
    print(f"Refreshing dataset {dataset_id} by syncing columns from source...")

    try:
        client.refresh_dataset(dataset_id)
        print("Successfully triggered refresh for dataset 35.")
        
        # Also set the main dttm column for good measure
        payload = {"main_dttm_col": "event_date"}
        client.update_dataset(dataset_id, payload)
        print("Successfully set 'main_dttm_col' to 'event_date'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    refresh_page_views_dataset()
