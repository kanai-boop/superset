import sys
from pathlib import Path

# Ensure the script can find other scripts in the same directory
sys.path.append(str(Path(__file__).parent))

from set_ga_metrics_directly import set_ga_dataset_metrics

# The new ID for the v_ga_sessions dataset is 26, found from the output of restore_assets.py
NEW_DATASET_ID = 26

print(f"--- Running metric fix for dataset ID: {NEW_DATASET_ID} ---")
set_ga_dataset_metrics(NEW_DATASET_ID)
print("--- Metric fix complete. ---")
