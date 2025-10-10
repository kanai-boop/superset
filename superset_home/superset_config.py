# superset_home/superset_config.py
# CSRF保護を一時的に無効にする (開発環境でのみ推奨)
WTF_CSRF_ENABLED = False

# APIドキュメントを有効にする (念のためここにも記述)
SUPERSET_WEBSERVER_API_ENABLED = True
SUPERSET_WEBSERVER_API_DOCS_ENABLED = True

FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,       # ネイティブフィルタ
    "DASHBOARD_NATIVE_FILTERS_SET": True,   # フィルタセット（プリセット）
    "DASHBOARD_CROSS_FILTERS": True,        # チャート間クロスフィルタ（任意）
    "ENABLE_TEMPLATE_PROCESSING": True      # Jinjaなど（任意）
}