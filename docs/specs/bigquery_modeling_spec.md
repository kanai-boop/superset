# BigQuery モデリング仕様（GA/広告統合）

## スキーマとビュー
- スキーマ: `analytics_456071139`
- ビュー:
  - `v_ga_sessions`（GA4 セッション基盤）
  - `v_ga_ads_performance`（GA4 × Ads 統合）
  - `v_ga_page_views`（GA4 PV抽出）
  - `v_ga_page_exits`（ページ離脱率計算）

## 日付列・時間軸の原則
- 可視化は DATE 列を使用（安定化のため TIMESTAMP ではなく DATE）。
- 計算列: `session_date AS CAST(event_date AS DATE)` を作成し `is_dttm: true`。
- データセット側で `main_dttm_col = session_date` を設定。

## チャネル分類（計算列）
- 列名: `channel_group`（STRING）
- 代表定義（簡略）:
```
CASE
  WHEN (source = 'google' AND medium = 'organic') OR (source = 'yahoo' AND medium = 'organic') THEN 'Organic Search'
  WHEN source IN ('google','bing') AND medium = 'cpc' THEN 'Paid Search'
  WHEN source IN ('facebook','twitter','instagram','line') AND medium = 'cpc' THEN 'Paid Social'
  WHEN source = 'youtube' AND medium = 'cpc' THEN 'Paid Video'
  WHEN medium = 'display' THEN 'Display'
  WHEN medium = 'video' THEN 'Paid Video'
  WHEN medium = 'social' THEN 'Organic Social'
  WHEN medium = 'email' THEN 'Email'
  WHEN medium = 'referral' THEN 'Referral'
  WHEN source = '(direct)' THEN 'Direct'
  ELSE 'Other'
END
```

## ビュー定義（v_ga_page_views）
```sql
CREATE OR REPLACE VIEW `winglish-gemini-cli.analytics_456071139.v_ga_page_views` AS
SELECT
  DATE(TIMESTAMP_MICROS(event_timestamp)) AS event_date,
  (SELECT value.int_value FROM UNNEST(event_params) WHERE key='ga_session_id') AS ga_session_id,
  user_pseudo_id,
  (SELECT value.string_value FROM UNNEST(event_params) WHERE key='page_location') AS page_location,
  REGEXP_EXTRACT((SELECT value.string_value FROM UNNEST(event_params) WHERE key='page_location'), r'^[^?]+') AS base_url,
  1 AS page_view
FROM `winglish-gemini-cli.analytics_456071139.events_*`
WHERE event_name = 'page_view';
```

## ビュー定義（v_ga_sessions）の主要追加
- `session_pageviews` (INTEGER): セッション内のPV数（`COUNTIF(event_name = 'page_view')`）
- この列により、セッションデータとPVデータを統合し、`Total Pageviews = SUM(session_pageviews)`メトリクスを作成可能
- `base_landing_page` (STRING): ランディングページURL（パラメータ除外版）
  - `REGEXP_EXTRACT(landing_page, r'^[^?]+')`でURLパラメータを除外
  - LP別分析でURLパラメータ違いの同一ページを正しく集約可能

## ビュー定義（v_ga_page_exits）
ページ離脱率を計算するビュー。セッション最終ページを特定し、ページごとの離脱数と離脱率を算出。

**離脱の定義**: セッション内の最後のpage_viewイベントが発生したページ

**主要ロジック**:
1. `ROW_NUMBER() OVER (PARTITION BY user_pseudo_id, session_id ORDER BY event_timestamp DESC)` で各セッションの最終ページを特定
2. 最終ページ（`reverse_order = 1`）を離脱としてカウント
3. ページごとに `離脱率 = 離脱数 / ページビュー数` を計算

**出力列**:
- `event_date`, `base_url`, `page_title`, `pageviews`, `exits`, `exit_rate`

## 指標定義（例）
- Sessions: `COUNT(DISTINCT unique_session_id)`
- Users: `COUNT(DISTINCT user_pseudo_id)`
- Revenue: `SUM(revenue)`
- Conversions: `SUM(conversions)`
- Conversion Rate: `SUM(conversions) / NULLIF(COUNT(DISTINCT unique_session_id), 0)`
- Pageviews: `SUM(page_view)`（PVビュー）
- Ads Cost: `SUM(ads_cost)`（統合ビュー）
- ROAS: `AVG(roas)`（運用により `SUM(revenue)/NULLIF(SUM(ads_cost),0)` も可）

## 品質チェック
- `session_date` の連続性（欠損日なし）
- `unique_session_id` の一意性
- 割り算は `NULLIF` で 0 除算保護

## クロスリージョン JOIN 対策
- GCS へエクスポート→同リージョンにインポートしてから結合する。

---

## BigQueryへの直接アクセス（ビュー作成・更新時）

### 方法A：Superset SQL Lab経由
- Supersetのデータベース設定で`allow_dml: true`を有効化
- SQL Lab（`/api/v1/sqllab/execute/`）でCREATE VIEW/ALTER VIEWを実行
- **制約**: BigQueryサービスアカウントに`bigquery.tables.create`権限（roles/bigquery.dataEditor）が必要

### 方法B：Python + google-cloud-bigquery（推奨）
1. **ライブラリインストール**:
   ```bash
   pip3 install --user google-cloud-bigquery
   ```

2. **認証設定**:
   ```python
   import os
   from google.cloud import bigquery
   
   # サービスアカウントキーのパスを設定
   creds_path = '/path/to/gcp_credentials.json'
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
   
   # BigQueryクライアント初期化
   client = bigquery.Client(project='winglish-gemini-cli')
   ```

3. **ビュー定義の取得**:
   ```python
   query = """
   SELECT view_definition 
   FROM `winglish-gemini-cli.analytics_456071139.INFORMATION_SCHEMA.VIEWS` 
   WHERE table_name = 'v_ga_sessions'
   """
   result = client.query(query).result()
   for row in result:
       print(row.view_definition)
   ```

4. **ビュー作成・更新**:
   ```python
   sql = """
   CREATE OR REPLACE VIEW `winglish-gemini-cli.analytics_456071139.v_ga_sessions` AS
   SELECT ...
   """
   client.query(sql).result()
   print("View updated successfully!")
   ```

### サービスアカウントキーの場所
- プロジェクト内パス: `docker/gcp_credentials.json`
- キー情報: `superset-bigquery-connector@winglish-gemini-cli.iam.gserviceaccount.com`

### 必要な権限
- `roles/bigquery.dataViewer` (データ閲覧)
- `roles/bigquery.jobUser` (クエリ実行)
- `roles/bigquery.dataEditor` (ビュー作成・更新) ※データセット単位で付与推奨
