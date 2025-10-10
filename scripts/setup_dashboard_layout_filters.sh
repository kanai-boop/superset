#!/usr/bin/env bash
set -euo pipefail

# Configure via env vars or defaults
BASE_URL=${BASE_URL:-${SUPERSET_BASE_URL:-http://localhost:8088}}
USERNAME=${USERNAME:-${SUPERSET_USERNAME:-admin}}
PASSWORD=${PASSWORD:-${SUPERSET_PASSWORD:-admin}}
DASHBOARD_ID=${DASHBOARD_ID:-14}

echo "Logging in to $BASE_URL as $USERNAME" >&2
LOGIN=$(curl -sS -w "\n%{http_code}\n" -X POST "$BASE_URL/api/v1/security/login" \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\",\"provider\":\"db\",\"refresh\":true}")
CODE=$(printf "%s" "$LOGIN" | tail -n1)
BODY=$(printf "%s" "$LOGIN" | sed '$d')
if [ "$CODE" != "200" ]; then echo "$BODY"; exit 1; fi
TOKEN=$(printf "%s" "$BODY" | jq -r '.access_token')

TITLE=$(curl -sS "$BASE_URL/api/v1/dashboard/$DASHBOARD_ID" -H "Authorization: Bearer $TOKEN" | jq -r '.result.dashboard_title // "Dashboard"')
OWNERS=$(curl -sS "$BASE_URL/api/v1/dashboard/$DASHBOARD_ID" -H "Authorization: Bearer $TOKEN" | jq -c '.result.owners | map(if type=="object" then .id else . end) | if length==0 then [1] else . end')

POS='{"DASHBOARD_VERSION_KEY":"v2","GRID_ID":{"id":"GRID_ID","type":"GRID","children":["ROW-1","ROW-2","ROW-3","ROW-4"]},"ROW-1":{"id":"ROW-1","type":"ROW","children":["COLUMN-1-1","COLUMN-1-2","COLUMN-1-3"],"meta":{"background":"BACKGROUND_TRANSPARENT"}},"ROW-2":{"id":"ROW-2","type":"ROW","children":["COLUMN-2-1","COLUMN-2-2","COLUMN-2-3"],"meta":{"background":"BACKGROUND_TRANSPARENT"}},"ROW-3":{"id":"ROW-3","type":"ROW","children":["COLUMN-3-1","COLUMN-3-2"],"meta":{"background":"BACKGROUND_TRANSPARENT"}},"ROW-4":{"id":"ROW-4","type":"ROW","children":["COLUMN-4-1"],"meta":{"background":"BACKGROUND_TRANSPARENT"}},"COLUMN-1-1":{"id":"COLUMN-1-1","type":"COLUMN","children":["CHART-264"],"meta":{"width":4}},"COLUMN-1-2":{"id":"COLUMN-1-2","type":"COLUMN","children":["CHART-265"],"meta":{"width":4}},"COLUMN-1-3":{"id":"COLUMN-1-3","type":"COLUMN","children":["CHART-266"],"meta":{"width":4}},"COLUMN-2-1":{"id":"COLUMN-2-1","type":"COLUMN","children":["CHART-267"],"meta":{"width":4}},"COLUMN-2-2":{"id":"COLUMN-2-2","type":"COLUMN","children":["CHART-268"],"meta":{"width":4}},"COLUMN-2-3":{"id":"COLUMN-2-3","type":"COLUMN","children":["CHART-269"],"meta":{"width":4}},"COLUMN-3-1":{"id":"COLUMN-3-1","type":"COLUMN","children":["CHART-270"],"meta":{"width":6}},"COLUMN-3-2":{"id":"COLUMN-3-2","type":"COLUMN","children":["CHART-271"],"meta":{"width":6}},"COLUMN-4-1":{"id":"COLUMN-4-1","type":"COLUMN","children":["CHART-272"],"meta":{"width":12}},"CHART-264":{"id":"CHART-264","type":"CHART","children":[],"meta":{"chartId":264,"sliceName":"Total Conversions","uuid":null,"width":4,"height":34}},"CHART-265":{"id":"CHART-265","type":"CHART","children":[],"meta":{"chartId":265,"sliceName":"Total Cost","uuid":null,"width":4,"height":34}},"CHART-266":{"id":"CHART-266","type":"CHART","children":[],"meta":{"chartId":266,"sliceName":"ROAS","uuid":null,"width":4,"height":34}},"CHART-267":{"id":"CHART-267","type":"CHART","children":[],"meta":{"chartId":267,"sliceName":"CTR","uuid":null,"width":4,"height":34}},"CHART-268":{"id":"CHART-268","type":"CHART","children":[],"meta":{"chartId":268,"sliceName":"Total Clicks","uuid":null,"width":4,"height":34}},"CHART-269":{"id":"CHART-269","type":"CHART","children":[],"meta":{"chartId":269,"sliceName":"Total Impressions","uuid":null,"width":4,"height":34}},"CHART-270":{"id":"CHART-270","type":"CHART","children":[],"meta":{"chartId":270,"sliceName":"Financial Trends (Daily)","uuid":null,"width":6,"height":50}},"CHART-271":{"id":"CHART-271","type":"CHART","children":[],"meta":{"chartId":271,"sliceName":"Traffic Trends (Daily)","uuid":null,"width":6,"height":50}},"CHART-272":{"id":"CHART-272","type":"CHART","children":[],"meta":{"chartId":272,"sliceName":"Campaign Performance","uuid":null,"width":12,"height":50}},"HEADER_ID":{"id":"HEADER_ID","type":"HEADER","meta":{"text":"__TITLE__"}},"ROOT_ID":{"id":"ROOT_ID","type":"ROOT","children":["HEADER_ID","GRID_ID"]}}'
POS=${POS/__TITLE__/$TITLE}

JM='{"native_filter_configuration":[{"id":"NATIVE_FILTER-$TIME_FILTER_ID","name":"Time Range","filterType":"filter_time","targets":[{"datasetId":27,"column":{"name":"segments_date"}},{"datasetId":30,"column":{"name":"__timestamp"}}],"defaultDataMask":{"extraFormData":{},"filterState":{"value":"Last 30 days"}},"scope":{"rootPath":["ROOT_ID"],"excluded":[]}},{"id":"NATIVE_FILTER-$CAMPAIGN_FILTER_ID","name":"Campaign","filterType":"filter_select","targets":[{"datasetId":27,"column":{"name":"campaign_base_campaign"}}],"defaultDataMask":{"extraFormData":{},"filterState":{"value":null}},"scope":{"rootPath":["ROOT_ID"],"excluded":[]},"controlValues":{"enableEmptyFilter":true,"multiSelect":true,"searchAllOptions":false,"inverseSelection":false}},{"id":"NATIVE_FILTER-$DEVICE_FILTER_ID","name":"Device","filterType":"filter_select","targets":[{"datasetId":27,"column":{"name":"segments_device"}},{"datasetId":30,"column":{"name":"device_category"}}],"defaultDataMask":{"extraFormData":{},"filterState":{"value":null}},"scope":{"rootPath":["ROOT_ID"],"excluded":[]},"controlValues":{"enableEmptyFilter":true,"multiSelect":true,"searchAllOptions":false,"inverseSelection":false}},{"id":"NATIVE_FILTER-$CHANNEL_MEDIUM_FILTER_ID","name":"Channel / Medium","filterType":"filter_select","targets":[{"datasetId":27,"column":{"name":"segments_ad_network_type"}},{"datasetId":30,"column":{"name":"traffic_medium"}}],"defaultDataMask":{"extraFormData":{},"filterState":{"value":null}},"scope":{"rootPath":["ROOT_ID"],"excluded":[]},"controlValues":{"enableEmptyFilter":true,"multiSelect":true,"searchAllOptions":false,"inverseSelection":false}}],"timed_refresh_immune_slices":[],"expanded_slices":{},"refresh_frequency":0,"color_scheme":"","label_colors":{},"shared_label_colors":[],"map_label_colors":{},"color_scheme_domain":[],"cross_filters_enabled":true}'

POS_PAYLOAD=$(jq -n --arg pos "$POS" --arg title "$TITLE" --argjson owners "$OWNERS" '{position_json: $pos, dashboard_title: $title, owners: $owners, published: true}')
echo "Applying position_json to dashboard $DASHBOARD_ID..." >&2
curl -sS -X PUT "$BASE_URL/api/v1/dashboard/$DASHBOARD_ID" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "$POS_PAYLOAD" | jq -r '.message // "ok"'

JM_PAYLOAD=$(jq -n --arg jm "$JM" --arg title "$TITLE" --argjson owners "$OWNERS" '{json_metadata: $jm, dashboard_title: $title, owners: $owners, published: true}')
echo "Applying filters to dashboard $DASHBOARD_ID..." >&2
curl -sS -X PUT "$BASE_URL/api/v1/dashboard/$DASHBOARD_ID" -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "$JM_PAYLOAD" | jq -r '.message // "ok"'

echo "Done. Dashboard ID: $DASHBOARD_ID" >&2
