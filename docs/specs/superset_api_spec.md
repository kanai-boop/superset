# Superset API 仕様（実運用ガイド）

- OpenAPIスナップショット: `superset/docs/specs/superset_openapi.json`
  - 命名ポリシー（次回以降）: `superset_openapi_<version>_<YYYY-MM-DD>.json`
  - 取得元: あなたの環境の `/swagger/v1`（有効な場合）または公式ドキュメント [Superset API docs](https://superset.apache.org/docs/api)

本ドキュメントは、Apache Superset を API 経由で操作する際の実用仕様と注意点をまとめたもの。自然言語からの自動チャート生成や自動復旧を目的に、再現可能なコマンド／ペイロード例を記す。

## 認証
- エンドポイント: `POST /api/v1/security/login`
- ペイロード:
  ```json
  {"username":"admin","password":"admin","provider":"db","refresh":true}
  ```
- レスポンス: `access_token`（JWT）。ヘッダは `Authorization: Bearer <JWT>`。
- 注意: トークン文字列に改行が混入すると 401/Bad Authorization。抽出は jq などで改行除去。

## データベース/データセット
- DB一覧: `GET /api/v1/database/`
- データセット作成: `POST /api/v1/dataset/`
  - 例: `{ "database": 2, "schema": "analytics_456071139", "table_name": "v_ga_sessions" }`
- データセット取得: `GET /api/v1/dataset/{id}`（`q={"columns":["columns","metrics"]}` 可）
- データセット更新: `PUT /api/v1/dataset/{id}`

### 重要な注意点（Columns/Metrics の PUT は上書き）
- `columns` や `metrics` を含む `PUT` は上書き挙動。
  - 新規列を足すときは「既存＋新規」の完全配列を送るか、差分適用の代替（リセット→再登録）を使う。
  - よくある失敗: `Columns missing in dataset`（既存列が消える）。

### 日付列・時間軸
- `main_dttm_col` を明示設定（例: `session_date`）。
- BigQuery で安定させるには計算列 `CAST(event_date AS DATE)` を作り `is_dttm=true` にする。
- 推奨手順: 計算列追加 → `main_dttm_col` 設定 → チャートを開いて Save（UI が新設定を認識）。

## チャート
- 作成: `POST /api/v1/chart/`
- 取得/検索: `GET /api/v1/chart/?q=...` （例: `{"filters":[{"col":"slice_name","opr":"chart_all_text","value":"..."}]}`）
- 更新: `PUT /api/v1/chart/{id}`
- 削除: `DELETE /api/v1/chart/{id}`

### params の取り扱い
- `params` は「JSON文字列」を期待。クライアント側で JSON→文字列化（`JSON.stringify` 相当）して送る。
- 例（Time-series Bar）:
  ```json
  {
    "slice_name": "GA: チャネル別 時系列 (New)",
    "viz_type": "echarts_timeseries_bar",
    "datasource_id": 28,
    "datasource_type": "table",
    "params": "{\"viz_type\":\"echarts_timeseries_bar\",\"datasource\":\"28__table\",\"x_axis\":\"session_date\",\"time_grain_sqla\":\"P1D\",\"metrics\":[\"Sessions\"],\"groupby\":[\"channel_group\"],\"stack\":true}"
  }
  ```

### 2軸（mixed_timeseries）の要点
- `metrics` と `metrics_b` を分ける。
- 軸割り当ては `yAxisIndex=0`, `yAxisIndexB=1`。
- セカンダリ軸の書式は `y_axis_format_secondary`。

### BigNumberチャートの期間合計表示
- **期間合計を表示するには `aggregation: "sum"` が必要**
  - デフォルト（未設定）または `aggregation: null` だと「Last Value」（最終日の値）が表示される
- **併せて `granularity_sqla: "event_date"` も設定**（エラー「Datetime column not provided」回避）
- **`time_grain_sqla` は `null` に設定**（時間軸での集約をしない = 期間全体の合計）
- 例:
  ```json
  {
    "viz_type": "big_number",
    "datasource": "28__table",
    "metric": "Users",
    "aggregation": "sum",
    "granularity_sqla": "event_date",
    "time_grain_sqla": null,
    "adhoc_filters": [{
      "expressionType": "SQL",
      "sqlExpression": "event_date >= DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH), MONTH) AND event_date < DATE_TRUNC(CURRENT_DATE(), MONTH)",
      "clause": "WHERE"
    }]
  }
  ```

### Mixed Timeseries（2軸）のフィルター設定
- **Query AとQuery Bで別々にフィルターを設定する必要がある**
  - Query A: `adhoc_filters`
  - Query B: `adhoc_filters_b`
- 両方に同じ期間フィルターを設定しないと、Query Bが全期間のデータを表示してしまう
- 例:
  ```json
  {
    "adhoc_filters": [{
      "clause": "WHERE",
      "subject": "event_date",
      "operator": "TEMPORAL_RANGE",
      "comparator": "Last month",
      "expressionType": "SIMPLE"
    }],
    "adhoc_filters_b": [{
      "clause": "WHERE",
      "subject": "event_date",
      "operator": "TEMPORAL_RANGE",
      "comparator": "Last month",
      "expressionType": "SIMPLE"
    }]
  }
  ```

## よくあるエラーと対処
- `Bad Authorization header`: トークン空／改行混入。抽出方法を見直す。
- `Unrecognized name: session_date`: 計算列未登録または `main_dttm_col` 未設定。
- `Columns missing in dataset`: `columns` 上書きで既存列が消失。完全配列で再登録。
- `One or more metrics already exist`: メトリクスはリセット→一括新規（空配列PUT→まとめてPUT）。
- `Datetime column not provided as part table configuration`: BigNumberチャートで `granularity_sqla` が未設定。`granularity_sqla: "event_date"` を設定。
- `No results were returned for this query`: MTD（今月）で今月のデータが存在しない場合に発生（正常）。または、SQLフィルターの日付条件がタイムゾーン問題でずれている可能性。年/月一致チェック（`EXTRACT(YEAR/MONTH FROM event_date) = EXTRACT(YEAR/MONTH FROM CURRENT_DATE())`）で回避可能。

## ダッシュボード
- `position_json` を API で書き換えるのは壊れやすい。配置は UI 操作が無難。

## セキュリティ/運用
- トンネルURL（ngrok/Cloudflare）は固定化推奨。ngrok は Reserved domain、Cloudflare は Named Tunnel。
- 機微情報（GCP認証）はファイルマウント or ADC を用い、APIペイロードには含めない。


