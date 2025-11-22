import json
import base64
import sys

# Read the raw JSON from stdin to avoid shell interpretation issues
raw_json_string = sys.stdin.read()

try:
    # Load the JSON to correctly handle escaped characters
    credentials = json.loads(raw_json_string)

    # Dump it back to a compact string without spaces
    compact_json_string = json.dumps(credentials, separators=(',', ':'))

    # Encode it in base64
    encoded_creds = base64.b64encode(compact_json_string.encode('utf-8'))

    # Print the final result to stdout
    print("\n\n--- Base64 Encoded Credentials ---", file=sys.stderr)
    print(encoded_creds.decode('utf-8'))
    print("--- End of Credentials ---", file=sys.stderr)

except json.JSONDecodeError as e:
    print(f"\nError: Invalid JSON provided. Make sure you pasted the entire JSON object. Details: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}", file=sys.stderr)
    sys.exit(1)
