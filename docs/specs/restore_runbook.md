# 復旧 Runbook（ゼロ構築/事故復旧）

## 前提
- Superset 稼働（UI/Health OK）
- ngrok or Cloudflare で外部到達可
- BigQuery 認証（ADC もしくはコンテナにファイルマウント）
- Python環境: `google-cloud-bigquery`インストール済み（`pip3 install --user google-cloud-bigquery`）
- サービスアカウントキー: `docker/gcp_credentials.json`（BigQuery直接アクセス用）

## ゼロからの構築（要点）
1) BigQuery DB 作成（ADC 前提）
2) データセット作成
   - `v_ga_sessions` / `v_ga_ads_performance`
3) 計算列と `main_dttm_col`
   - `session_date = CAST(event_date AS DATE)`（`is_dttm: true`）
   - `channel_group` を追加
   - `main_dttm_col = session_date`
4) メトリクス
   - セッション系（Sessions, Users, Conversions など）
   - 広告系（ads_cost, roas）
5) チャート作成（テンプレ参照）

## 事故復旧（DBリセット/列不整合 など）
- 症状: `Unrecognized name: session_date` / `Columns missing in dataset` / `Metric 'X' does not exist`
- 対処パターン:
  1. 計算列再追加 → `main_dttm_col` 再設定
  2. `metrics: []` でリセット → 必要メトリクス再登録
  3. データセットを削除→再作成（最終手段）
- ダッシュボード配置は UI で行う（`position_json` API は不安定）

## 検証
- 代表 6 チャートがエラーなく実行・保存できること
- ダッシュボードに配置後、Time range フィルターで連動

---

## BigQueryビュー作成・更新（Python経由）

SupersetのSQL Lab経由でビュー作成できない場合や、複雑なビュー定義を更新する場合は、Python + google-cloud-bigqueryで直接BigQueryにアクセスする。

### 手順

1. **ライブラリインストール**（初回のみ）:
   ```bash
   pip3 install --user google-cloud-bigquery
   ```

2. **スクリプト作成例**（ビュー定義取得）:
   ```python
   import os
   from google.cloud import bigquery
   
   # 認証設定
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/naruhitokanai/superset/superset/docker/gcp_credentials.json'
   client = bigquery.Client(project='winglish-gemini-cli')
   
   # ビュー定義取得
   query = """
   SELECT view_definition 
   FROM `winglish-gemini-cli.analytics_456071139.INFORMATION_SCHEMA.VIEWS` 
   WHERE table_name = 'v_ga_sessions'
   """
   for row in client.query(query).result():
       print(row.view_definition)
   ```

3. **スクリプト作成例**（ビュー更新）:
   ```python
   import os
   from google.cloud import bigquery
   
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/Users/naruhitokanai/superset/superset/docker/gcp_credentials.json'
   client = bigquery.Client(project='winglish-gemini-cli')
   
   sql = """
   CREATE OR REPLACE VIEW `winglish-gemini-cli.analytics_456071139.v_ga_sessions` AS
   WITH session_events AS (...)
   SELECT ...
   """
   client.query(sql).result()
   print("✓ View updated successfully!")
   ```

4. **実行**:
   ```bash
   python3 /tmp/update_view.py
   ```

5. **Superset側でリフレッシュ**:
   - API: `POST /api/v1/dataset/{id}/refresh`
   - UI: Dataset編集 → 「Sync Columns from Source」

### 注意点
- サービスアカウントキー（`gcp_credentials.json`）は機密情報。Gitにコミットしない（`.gitignore`確認）
- ビュー更新後は必ずSupersetでデータセットをリフレッシュ（新しい列を認識させる）
- `columns` PUT は上書き動作なので、計算列追加はビュー側で行うのが安全
