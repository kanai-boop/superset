# データセット契約（Contracts）

本書はダッシュボード/自動生成の前提となるデータセット仕様の“契約”を明示する。

## v_ga_sessions（IDは環境で異なる）
- 必須物理列
  - `event_date` (DATE or TIMESTAMP)
  - `unique_session_id` (STRING)
  - `user_pseudo_id` (STRING)
  - `session_pageviews` (INTEGER) - セッション内のPV数（`COUNTIF(event_name = 'page_view')`）
  - `landing_page` (STRING) - ランディングページURL（パラメータ付き）
  - `base_landing_page` (STRING) - ランディングページURL（パラメータ除外版、`REGEXP_EXTRACT(landing_page, r'^[^?]+')`）
  - `device_category` (STRING) - デバイス種類（mobile, tablet, desktop, smart tv）
  - `total_engagement_time_msec` (INTEGER) - エンゲージメント時間（ミリ秒）
  - `is_engaged_session` (BOOLEAN) - エンゲージセッションフラグ
  - `new_vs_returning` (STRING) - "New User" または "Returning User"
  - `source`, `medium`, `campaign` (STRING) - トラフィックソース
  - `conversions` (INTEGER), `revenue` (FLOAT) - CV/収益
- 必須計算列
  - `session_date = CAST(event_date AS DATE)`（`is_dttm: true`）
  - `channel_group`（上位チャネル分類の CASE）
- 必須メトリクス
  - `Sessions = COUNT(DISTINCT unique_session_id)`
  - `Users = COUNT(DISTINCT user_pseudo_id)`
  - `New Users = SUM(CASE WHEN new_vs_returning = 'new' THEN 1 ELSE 0 END)`
  - `Total Pageviews = SUM(session_pageviews)`（PV数合計）
  - `Pageviews per Session = AVG(session_pageviews)`（PV数/セッション）
  - `Revenue = SUM(revenue)`（任意）
  - `Conversions = SUM(conversions)`（任意）
  - `Conversion Rate = SUM(conversions) / NULLIF(COUNT(DISTINCT unique_session_id), 0)`（任意）
  - `Avg Engagement Time (sec) = AVG(total_engagement_time_msec) / 1000`
  - `Engagement Rate = SUM(CASE WHEN is_engaged_session THEN 1 ELSE 0 END) / NULLIF(COUNT(DISTINCT unique_session_id), 0)`
  - `Engaged Sessions = SUM(CASE WHEN is_engaged_session THEN 1 ELSE 0 END)`
- 時間軸
  - `main_dttm_col = session_date`
  - ダッシュボード連動の安定化のため、`event_date` を `is_dttm: true`（Temporal）にも設定し、時系列系チャートの X‑axis は `event_date` を優先的に使用する。

### 検証（Validate）
- 列存在チェック: 上記列が Explore で選択できること
- メトリクス存在チェック: 上記メトリクスが Metrics に表示されること
- 代表クエリが実行成功（Last 90 days, groupby channel_group）
- `base_landing_page`列が正しくURLパラメータを除外していること
- `new_vs_returning`列で新規/リピーターが正しく分類されていること

### クロス分析活用
このデータセットは以下のクロス分析に使用される:
- **チャネル × デバイス**: `source`, `medium`, `device_category`でグループ化
- **チャネル × 地域**: `source`, `geo_region`でグループ化（日本国内）
- **チャネル × 時間帯**: `source`, `session_hour`でグループ化
- **チャネル × 新規/リピーター**: `source`, `new_vs_returning`でグループ化
- **チャネル × 曜日**: `source`, `day_of_week`でグループ化
- 主要分析軸: source（流入元）を基準に各セグメントと組み合わせ

## v_ga_ads_performance（IDは環境で異なる）
- 必須物理列
  - `event_date` (DATE)
  - `ads_cost` (FLOAT)
  - `roas` (FLOAT) ※式で算出する場合は不要
- 必須メトリクス
  - `ads_cost = SUM(ads_cost)`
  - `roas = AVG(roas)`（または `SUM(revenue)/NULLIF(SUM(ads_cost),0)`）
- 時間軸
  - `main_dttm_col = event_date`

### 検証（Validate）
- 2軸チャートで `ads_cost`（左軸）, `roas`（右軸）が描画できること
- 直近 90 日でクエリがタイムアウトせず応答

## v_ga_page_views（IDは環境で異なる）
- 必須物理列
  - `event_date` (DATE) - Temporal列（`is_dttm: true`）
  - `page_view` (INTEGER)
  - `user_pseudo_id` (STRING)
  - `ga_session_id` (INTEGER)
  - `page_location` (STRING) - 完全なURL
  - `base_url` (STRING) - URLパラメーター除外（`REGEXP_EXTRACT(page_location, r'^[^?]+')`）
- 必須メトリクス
  - `Pageviews = SUM(page_view)`
- 時間軸
  - `main_dttm_col = event_date`
- ビュー定義
  - BigQuery側で `analytics_456071139.v_ga_page_views` を作成
  - GA4 events_* テーブルから `event_name = 'page_view'` を抽出
  - `base_url` 列でURLパラメーター（`?`以降）を除外し、同一ページのPVを集約可能に

### 検証（Validate）
- BigNumberチャートで `Pageviews` メトリクスが期間合計として表示されること
- `event_date` が Temporal として認識され、ダッシュボード時間フィルターでエラーが出ないこと
- 横棒チャートで `base_url` を使い、URLパラメーターが除外されてPV数が正しく集計されること

## v_ga_page_exits（IDは環境で異なる）
- 必須物理列
  - `event_date` (DATE) - Temporal列（`is_dttm: true`）
  - `base_url` (STRING) - URLパラメーター除外
  - `page_title` (STRING) - ページタイトル
  - `pageviews` (INTEGER) - ページビュー数
  - `exits` (INTEGER) - 離脱数（セッション最終ページとしてのPV数）
  - `exit_rate` (FLOAT) - 離脱率（`exits / pageviews`）
- 必須メトリクス
  - `Total Pageviews = SUM(pageviews)`
  - `Total Exits = SUM(exits)`
  - `Exit Rate = SUM(exits) / NULLIF(SUM(pageviews), 0)`
- 時間軸
  - `main_dttm_col = event_date`
- ビュー定義
  - セッション最終ページを特定し、ページごとの離脱数/離脱率を計算
  - `ROW_NUMBER() OVER (PARTITION BY session ORDER BY event_timestamp DESC)` で最終ページを判定

### 検証（Validate）
- テーブルチャートでpage_title/base_url別の離脱率が表示されること
- 時系列チャートでPV数と離脱率が2軸で表示されること
- 散布図でPV数（X軸）vs 離脱率（Y軸）の関係が可視化されること

## v_ga_ads_performance（ID: 27）
- 必須物理列
  - `event_date` (DATE) - Temporal列（`is_dttm: true`）
  - `sessions` (INTEGER) - セッション数
  - `users` (INTEGER) - ユーザー数
  - `revenue` (FLOAT) - 収益
  - `conversions` (INTEGER) - コンバージョン数
  - `ads_cost` (FLOAT) - 広告費
  - `ads_clicks` (INTEGER) - クリック数
  - `ads_impressions` (INTEGER) - インプレッション数
  - `roas` (FLOAT) - ROAS（ビュー内で計算済み）
  - `cac` (FLOAT) - CAC（ビュー内で計算済み）
- 必須メトリクス（アドホック定義）
  - `Total Cost = SUM(ads_cost)`
  - `Total Clicks = SUM(ads_clicks)`
  - `Total Impressions = SUM(ads_impressions)`
  - `Total Conversions = SUM(conversions)`
  - `Total Revenue = SUM(revenue)`
  - `CTR = SUM(ads_clicks) / NULLIF(SUM(ads_impressions), 0) * 100`
  - `CPC = SUM(ads_cost) / NULLIF(SUM(ads_clicks), 0)`
  - `ROAS = SUM(revenue) / NULLIF(SUM(ads_cost), 0)`
  - `CPA = SUM(ads_cost) / NULLIF(SUM(conversions), 0)`
- 時間軸
  - `main_dttm_col = event_date`
- データ期間
  - 2025-08-07 ～ 2025-10-09（約2ヶ月、231レコード）

### 検証（Validate）
- BigNumberチャートで今月のコスト・クリック・CVが表示されること
- 先月比（％）が正しく計算されること
- ROASとCPAが0除算エラーなく表示されること
- 時系列チャートでコストとクリックが2軸で表示されること

## v_ga_content_performance（ID: 37）
- 必須物理列
  - `event_date` (DATE) - Temporal列（`is_dttm: true`）
  - `page_title` (STRING) - ページタイトル
  - `base_page_url` (STRING) - URLパラメータ除外後のURL
  - `pageviews` (INTEGER) - ページビュー数
  - `unique_users` (INTEGER) - ユニークユーザー数
  - `sessions` (INTEGER) - セッション数
  - `avg_engagement_sec` (FLOAT) - 平均エンゲージメント時間（秒）
  - `entrances` (INTEGER) - エントリー数（セッションの最初のページ）
  - `exits` (INTEGER) - エグジット数（セッションの最後のページ）
  - `exit_rate` (FLOAT) - 離脱率（%）
  - `sessions_with_conversion` (INTEGER) - CVがあったセッション数
  - `total_conversions` (INTEGER) - 総コンバージョン数
  - `session_conversion_rate` (FLOAT) - セッションCVR（%）
- 必須メトリクス（アドホック定義）
  - `Total Pageviews = SUM(pageviews)`
  - `Total Users = SUM(unique_users)`
  - `Total Sessions = SUM(sessions)`
  - `Avg Engagement = AVG(avg_engagement_sec)`
  - `Total Entrances = SUM(entrances)`
  - `Total Exits = SUM(exits)`
  - `Avg Exit Rate = AVG(exit_rate)`
  - `Total Conversions = SUM(total_conversions)`
  - `Avg CVR = AVG(session_conversion_rate)`
- 時間軸
  - `main_dttm_col = event_date`
- ビュー定義
  - page_viewイベントから各ページのパフォーマンス指標を集計
  - エントリー/エグジット判定（`ROW_NUMBER() OVER (PARTITION BY session ORDER BY event_timestamp ASC/DESC)`）
  - CV関連付け（session単位でJOIN）
  - 離脱率とセッションCVRを計算

### 検証（Validate）
- 人気コンテンツランキングでページタイトル別PVが表示されること
- エンゲージメント時間で50PV以上のページがフィルターされること
- パフォーマンステーブルで全指標（PV/Users/Sessions/Engagement/Exit Rate/CVR）が表示されること
- Bubbleチャートでエンゲージメント（X軸）×CVR（Y軸）×PV（サイズ）が表示されること
- 月別トレンドでTOP5ページの推移が折れ線で表示されること
- エントリー・エグジットテーブルでランディング/離脱パターンが分析できること
