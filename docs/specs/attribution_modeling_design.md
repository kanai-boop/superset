# アトリビューションパス設計書

## 概要
GA4のアトリビューションパスレポートをSupersetで再現するための設計。
コンバージョンまでのユーザージャーニーを可視化し、各タッチポイントの貢献度を分析する。

## データモデル設計

### BigQueryビュー: v_ga_attribution_paths

#### 目的
- コンバージョンに至ったユーザーの全セッション経路を構築
- 早期・中間・後期タッチポイントを分類
- パス文字列（"Organic Search > Email > Direct"）を生成
- CVまでの日数、タッチポイント数を計算

#### SQL実装

```sql
CREATE OR REPLACE VIEW `winglish-gemini-cli.analytics_456071139.v_ga_attribution_paths` AS
WITH 
-- ステップ1: コンバージョンイベントを特定
conversions AS (
  SELECT 
    user_pseudo_id,
    event_timestamp AS conversion_timestamp,
    DATE(TIMESTAMP_MICROS(event_timestamp)) AS conversion_date,
    (SELECT value.double_value FROM UNNEST(event_params) WHERE key='value') AS conversion_value
  FROM `winglish-gemini-cli.analytics_456071139.events_*`
  WHERE event_name = 'purchase' -- または key_events フィールドで判定
),

-- ステップ2: コンバージョン前の全セッションを取得
session_journey AS (
  SELECT 
    s.user_pseudo_id,
    c.conversion_timestamp,
    c.conversion_date,
    c.conversion_value,
    s.session_id,
    s.session_start_timestamp,
    s.channel_group,
    s.source,
    s.medium,
    s.revenue,
    ROW_NUMBER() OVER (
      PARTITION BY s.user_pseudo_id, c.conversion_timestamp 
      ORDER BY s.session_start_timestamp
    ) AS session_position,
    COUNT(*) OVER (
      PARTITION BY s.user_pseudo_id, c.conversion_timestamp
    ) AS total_sessions
  FROM v_ga_sessions s
  INNER JOIN conversions c 
    ON s.user_pseudo_id = c.user_pseudo_id
    AND s.session_start_timestamp < c.conversion_timestamp
),

-- ステップ3: タッチポイント分類（Early 25% / Middle 50% / Late 25%）
touchpoint_classified AS (
  SELECT 
    *,
    CASE 
      WHEN session_position <= CAST(total_sessions * 0.25 AS INT64) AND session_position >= 1 THEN 'Early'
      WHEN session_position > CAST(total_sessions * 0.75 AS INT64) THEN 'Late'
      ELSE 'Middle'
    END AS touchpoint_phase,
    DATE_DIFF(
      DATE(TIMESTAMP_MICROS(conversion_timestamp)), 
      DATE(session_start_timestamp), 
      DAY
    ) AS days_from_first_touch
  FROM session_journey
),

-- ステップ4: パス文字列を構築
path_aggregated AS (
  SELECT 
    user_pseudo_id,
    conversion_timestamp,
    conversion_date,
    conversion_value,
    total_sessions AS touchpoint_count,
    MAX(days_from_first_touch) AS days_to_conversion,
    STRING_AGG(channel_group, ' > ' ORDER BY session_position) AS full_path,
    -- 各フェーズの最初のチャネルを取得
    STRING_AGG(
      CASE WHEN touchpoint_phase = 'Early' THEN channel_group END, 
      ', ' 
      ORDER BY session_position
    ) AS early_channels,
    STRING_AGG(
      CASE WHEN touchpoint_phase = 'Middle' THEN channel_group END, 
      ', ' 
      ORDER BY session_position
    ) AS middle_channels,
    STRING_AGG(
      CASE WHEN touchpoint_phase = 'Late' THEN channel_group END, 
      ', ' 
      ORDER BY session_position
    ) AS late_channels
  FROM touchpoint_classified
  GROUP BY user_pseudo_id, conversion_timestamp, conversion_date, conversion_value, total_sessions
),

-- ステップ5: Sankey用の from → to ペアを生成
sankey_edges AS (
  SELECT 
    user_pseudo_id,
    conversion_timestamp,
    channel_group AS from_channel,
    LEAD(channel_group) OVER (
      PARTITION BY user_pseudo_id, conversion_timestamp 
      ORDER BY session_position
    ) AS to_channel,
    session_position
  FROM touchpoint_classified
)

-- 最終出力: 2つのデータセット用に UNION
-- データセット1: パス単位の集計
SELECT 
  conversion_date,
  full_path,
  touchpoint_count,
  COUNT(DISTINCT user_pseudo_id) AS conversions,
  SUM(conversion_value) AS revenue,
  AVG(days_to_conversion) AS avg_days_to_conversion,
  AVG(touchpoint_count) AS avg_touchpoint_count,
  early_channels,
  middle_channels,
  late_channels,
  NULL AS from_channel,
  NULL AS to_channel,
  'path_summary' AS data_type
FROM path_aggregated
GROUP BY conversion_date, full_path, touchpoint_count, early_channels, middle_channels, late_channels

UNION ALL

-- データセット2: Sankey用の遷移データ
SELECT 
  DATE(TIMESTAMP_MICROS(s.conversion_timestamp)) AS conversion_date,
  NULL AS full_path,
  NULL AS touchpoint_count,
  COUNT(DISTINCT s.user_pseudo_id) AS conversions,
  NULL AS revenue,
  NULL AS avg_days_to_conversion,
  NULL AS avg_touchpoint_count,
  NULL AS early_channels,
  NULL AS middle_channels,
  NULL AS late_channels,
  s.from_channel,
  s.to_channel,
  'sankey_edge' AS data_type
FROM sankey_edges s
WHERE s.to_channel IS NOT NULL
GROUP BY conversion_date, s.from_channel, s.to_channel;
```

#### 出力スキーマ

**パス集計モード** (`data_type = 'path_summary'`):
- `conversion_date` (DATE): コンバージョン日
- `full_path` (STRING): 完全な経路（例: "Organic Search > Email > Direct"）
- `touchpoint_count` (INTEGER): タッチポイント数
- `conversions` (INTEGER): コンバージョン数
- `revenue` (FLOAT): 購入による収益
- `avg_days_to_conversion` (FLOAT): 平均日数
- `avg_touchpoint_count` (FLOAT): 平均タッチポイント数
- `early_channels` (STRING): 早期タッチポイントのチャネル
- `middle_channels` (STRING): 中間タッチポイントのチャネル
- `late_channels` (STRING): 後期タッチポイントのチャネル

**Sankey遷移モード** (`data_type = 'sankey_edge'`):
- `from_channel` (STRING): 遷移元チャネル
- `to_channel` (STRING): 遷移先チャネル
- `conversions` (INTEGER): この遷移を経たCV数

## Superset実装

### データセット作成

**データセット1**: `attribution_paths` (ID未定)
- **フィルター**: `data_type = 'path_summary'`
- **主要列**: `conversion_date`, `full_path`, `early_channels`, `middle_channels`, `late_channels`
- **主要メトリクス**:
  - `Total Conversions = SUM(conversions)`
  - `Total Revenue = SUM(revenue)`
  - `Avg Days = AVG(avg_days_to_conversion)`
  - `Avg Touchpoints = AVG(avg_touchpoint_count)`

**データセット2**: `attribution_sankey` (ID未定)
- **フィルター**: `data_type = 'sankey_edge'`
- **主要列**: `from_channel`, `to_channel`
- **主要メトリクス**: `Flow Volume = SUM(conversions)`

### チャート構成

#### チャート1: 早期タッチポイント貢献度（横棒）
```json
{
  "viz_type": "echarts_timeseries_bar",
  "datasource": "attribution_paths",
  "x_axis": "early_channels",
  "metrics": ["Total Conversions"],
  "groupby": [],
  "orientation": "horizontal",
  "row_limit": 10,
  "adhoc_filters": [{
    "clause": "WHERE",
    "sqlExpression": "early_channels IS NOT NULL",
    "expressionType": "SQL"
  }],
  "percent_metrics": ["Total Conversions"]
}
```

#### チャート2: 中間タッチポイント貢献度（横棒）
- `x_axis: "middle_channels"`に変更
- その他は同様

#### チャート3: 後期タッチポイント貢献度（横棒）
- `x_axis: "late_channels"`に変更
- その他は同様

#### チャート4: コンバージョン上位経路（テーブル）
```json
{
  "viz_type": "table",
  "datasource": "attribution_paths",
  "query_mode": "aggregate",
  "groupby": ["full_path"],
  "metrics": [
    "Total Conversions",
    "Total Revenue",
    "Avg Days",
    "Avg Touchpoints"
  ],
  "adhoc_filters": [],
  "row_limit": 10,
  "order_desc": true,
  "order_by_cols": ["Total Conversions"],
  "percent_metrics": ["Total Conversions", "Total Revenue"]
}
```

#### チャート5: 経路フロー（Sankey）※オプション
```json
{
  "viz_type": "sankey",
  "datasource": "attribution_sankey",
  "groupby": ["from_channel", "to_channel"],
  "metric": "Flow Volume",
  "row_limit": 100
}
```

## 実装の段階

### Phase 1: 基本ビューの作成と検証 ✅ 完了
1. ✅ BigQueryで`v_ga_attribution_paths`を作成
   - コンバージョンイベント: `conversion_event_page_view`（1,193件/週）
   - `v_ga_sessions`に`channel_group`列がないため、SQL内でチャネル分類ロジックを実装
   - パス集計データ: 1,039行（7,258 CV）
   - Sankey遷移データ: 157行（1,817 CV）
2. ✅ 結果を確認
   - ほとんどが単一タッチポイント（Referral）
   - 平均コンバージョン日数: 0日（即時CV）
   - マルチタッチパスも存在（157パターン）
3. ⏭️ 次: Supersetでデータセットを登録

### Phase 2: 基本チャートの作成 ✅ 完了
1. ✅ データセット登録（ID: 35）
   - `conversion_date`がTemporalに自動設定
   - メトリクス追加: Total Conversions, Avg Days to CV, Avg Touchpoints
2. ✅ GA4スタイルのタッチポイント別チャート作成
   - Chart 245: 早期タッチポイント貢献度（First 25%）
   - Chart 246: 中間タッチポイント貢献度（Middle 50%）
   - Chart 247: 後期タッチポイント貢献度（Last 25%）
3. ✅ 分析チャート作成
   - Chart 242: アトリビューションパスTOP20（テーブル）
   - Chart 244: タッチポイント数分布（棒グラフ）
4. ✅ ダッシュボード作成（ID: 17）
   - 「アトリビューションパス分析」
   - 5つのチャートを配置

### Phase 3: 高度な可視化 ✅ 完了
1. ✅ 時系列分析チャート作成
   - Chart 248: 月別コンバージョン推移（折れ線）
2. ✅ チャネル階層可視化
   - Chart 249: Sunburstチャート（Early → Middle → Late）
3. ✅ チャネル遷移フロー
   - Chart 250: Chordダイアグラム（from_channel → to_channel）
4. ✅ コンバージョンファネル
   - Chart 251: タッチポイント数別ファネル（1-5タッチポイント）
5. ✅ チャネル別パフォーマンス分析
   - Chart 252: チャネル別平均コンバージョン日数（横棒）
6. ✅ ダッシュボード更新
   - 合計10チャートを5行のレイアウトで配置
   - 「アトリビューションパス分析（拡張版）」として完成

**注**: Sankeyダイアグラムは標準プラグインに含まれていないため、代替としてChordダイアグラム（後にテーブル形式に変更）を使用

## Phase 4: ページ経路分析（Path Exploration） ✅ 完了

GA4の「経路データ探索」機能を実装。ユーザーがどのページから訪問し、どのような経路を辿ってコンバージョンに至ったかを分析。

### BigQueryビュー作成
1. ✅ `v_ga_page_paths` ビュー作成
   - コンバージョン前のpage_viewイベントを時系列で追跡
   - 始点（最初のページ）、終点（最後のページ）を特定
   - From → To のページ遷移を生成
   - データ規模:
     - 始点: 83種類（6,500 CVs）
     - 終点: 1,843種類（9,638 CVs）
     - 遷移: 895パターン（3,761 CVs）

### Supersetチャート作成
2. ✅ Dataset 36: `v_ga_page_paths` 登録
3. ✅ Chart 254: 始点ページ TOP10（最初に訪問したページ）
4. ✅ Chart 255: 終点ページ TOP10（CV直前のページ）
5. ✅ Chart 256: ページ遷移テーブル（From → To TOP20）
6. ✅ Chart 257: ページ遷移Sunburst（視覚的なフロー）

### ダッシュボード作成
7. ✅ Dashboard 18: 「ページ経路分析（Path Exploration）」
   - 4チャートを配置（UIで手動レイアウト調整が必要）
   - GA4の経路データ探索機能を完全再現

### 詳細ドキュメント
- `page_path_exploration_design.md`: 完全な設計・実装ドキュメント

## 注意点

### データ量の懸念
- ユーザージャーニーの計算は重い処理
- 初回は直近1ヶ月のデータに絞って検証
- 本番運用時はマテリアライズドビューまたはスケジュールクエリでの定期更新を推奨

### パス文字列の長さ
- 長いパス（10+ タッチポイント）は表示が崩れる可能性
- TOP10表示で対処、または省略表示の実装

### チャネル分類の精度
- `v_ga_sessions`の`channel_group`が正確に設定されていることが前提
- 必要に応じてチャネル分類ロジックを見直し

### コンバージョン定義
- **実装版**: `event_name = 'conversion_event_page_view'`を使用
- `purchase`イベントは現在のデータに存在しない
- 必要に応じてCTE `conversions`の条件を変更

## トラブルシューティング

### 「Early/Middle/Late が NULL」
- **原因**: タッチポイントが1つのみ（25%境界の計算で全てが除外）
- **対処**: 単一タッチポイントの場合は"Late"に分類するロジックを追加

### 「パスが空白」
- **原因**: セッションデータとコンバージョンの紐付けが失敗
- **対処**: `v_ga_sessions`と`events_*`のタイムスタンプ形式を確認

### 「Sankeyが表示されない」
- **原因**: プラグインが有効化されていない
- **対処**: `superset-ui/legacy-plugin-chart-sankey`をインストール・登録

