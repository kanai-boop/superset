# トラブルシュート（既知エラーと即時対処）

## 認証/ネットワーク
- `Bad Authorization header`: トークン空/改行混入 → jq で `-r '.access_token'`
- トンネル切断: ngrok/Cloudflare を再起動（URLが変わる場合あり）

## データセット/列
- `Unrecognized name: session_date`
  - `session_date = CAST(event_date AS DATE)` を計算列で追加（`is_dttm: true`）
  - `main_dttm_col = session_date` に設定
- `Columns missing in dataset: [...]`
  - `columns` PUT が上書き → 既存＋追加の“完全配列”で再登録
  - もしくは一度データセット作り直し
- 計算列がテンポラル扱いされない
  - 一部Viz（Big Number等）で計算列が時系列として解釈されない場合がある。
  - 対策: 物理列 `event_date` を `is_dttm: true` にし、時系列系チャートの Temporal X‑Axis を `event_date` に切替える。

## メトリクス
- `Metric 'X' does not exist`
  - `metrics: []` でリセット → 必要メトリクスを一括再登録

## チャート
- 2軸が効かない
  - `metrics` と `metrics_b` を分離
  - `yAxisIndex: 0`, `yAxisIndexB: 1` を明示
  - secondary の書式は `y_axis_format_secondary`
- Big Number の比較が効かない/期間が安定しない
  - `compare_lag: 1`, `comparison_type: 'percentage'`, `show_delta/percent: true`
  - 期間は `time_range` ではなく `adhoc_filters` の SQL で `event_date` を基準に絞ると安定

## ダッシュボード
- 配置が反映されない
  - `position_json` の API 更新は相性があるため、UIで配置→Save

## BigNumberチャート
- 期間合計が表示されず、最終日の値だけが表示される
  - **原因**: `aggregation` パラメータが `"Last Value"` または未設定（デフォルトで Last Value になる）
  - **解決**: `aggregation: "sum"` を明示的に設定
  - **併せて**: `granularity_sqla: "event_date"` も設定（エラー回避のため）
  - **注意**: `time_grain_sqla` は `null` に設定（時間軸での集約をしない = 期間全体の合計）
- MTD（今月）が「No results」になる
  - **原因**: 今月のデータが存在しない（例: 11/1時点で最終データが10/31まで）
  - **対処**: 仕様として正常。または、MTDフィルターを「年/月一致」方式（`EXTRACT(YEAR/MONTH FROM event_date) = EXTRACT(YEAR/MONTH FROM CURRENT_DATE())`）に変更してタイムゾーン問題を回避

## カテゴリ別横棒チャート
- 横棒チャートで月別に分かれてしまう
  - **原因**: `echarts_timeseries_bar`で`x_axis`に時間列、`time_grain_sqla`が設定されている
  - **解決**: `x_axis`をカテゴリ列（`channel_group`/`medium`/`source`）に変更し、`groupby: []`、`stack: null`で非時系列集計にする
- `echarts_bar`が「This visualization type is not supported」エラー
  - **原因**: Supersetバージョンやプラグイン設定で`echarts_bar`が利用できない
  - **対処**: `echarts_timeseries_bar`を使い、`x_axis`にカテゴリ列を指定することでカテゴリ別チャートとして機能させる

## 時系列比較チャート
- 「An enclosed time range must be specified when using a Time Comparison」エラー
  - **原因**: `time_compare`を使う際に`adhoc_filters`の期間が「No filter」になっている
  - **解決**: 具体的な期間（`"Last month"`/`"This month"`など）を`adhoc_filters`で指定
- 「Time delta is ambiguous. Please specify [1 month ago] or [1 month later]」エラー
  - **原因**: `time_compare`の形式が不正（例: `["1 month"]`）
  - **解決**: 正しい形式で指定（例: `["1 month ago"]`）
- Mixed Timeseries（2軸）でQuery Bにフィルターが効かない
  - **原因**: `adhoc_filters`がQuery Aのみに適用され、Query Bには別途指定が必要
  - **解決**: `adhoc_filters_b`に同じ期間フィルターを設定

## URLパラメーター除外
- 上位ページチャートでURLパラメーター（`?`以降）が異なるだけの同一ページが別々に集計される
  - **原因**: `page_location`にURLパラメーターが含まれている
  - **解決**: BigQueryビューで`base_url = REGEXP_EXTRACT(page_location, r'^[^?]+')`列を追加し、チャートで`base_url`を使用
  - **注意**: Supersetの`columns` PUT は上書き動作なので、ビュー側で列を追加するのが安全

## バブルチャート/散布図
- 「Please use 3 different metric labels」エラー
  - **原因**: `x`, `y`, `size`に同じメトリクスが使用されている
  - **解決**: 3つの異なるメトリクスを指定（例: `x="Total Pageviews"`, `y="Exit Rate"`, `size="Total Exits"`）
- 「Empty query?」エラー
  - **原因**: `echarts_scatter`が利用できない、またはparamsが不正
  - **対処**: `viz_type: "bubble"`を使用（Bubble chartは安定している）

## Google Ads チャート
- 「No results」（BigNumber KPIs）
  - **原因**: 今月（11月）のデータが存在しない（最新は2025-10-09）
  - **解決**: フィルターを10月（`event_date >= '2025-10-01' AND event_date < '2025-11-01'`）に変更
- ROASやCPAが計算できない
  - **原因**: コンバージョンまたは収益がゼロ（10月データ）
  - **解決**: 
    - ROAS/CPAは全期間データで表示（`adhoc_filters: []`）
    - CPAの代わりにCPC（クリック単価）を使用
- テーブルチャートが全てN/A
  - **原因**: TEMPORAL_RANGEフィルターが適切に機能していない
  - **解決**: SQLフィルター（`event_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)`）またはフィルターなし（全期間）に変更
- 通貨表示
  - **デフォルト**: `$,.0f`（ドル）
  - **修正**: `¥,.0f`（円）に変更
  - **問題**: `¥`記号が「Invalid format」エラー
  - **解決**: フォーマットから記号を削除（`,d`や`,.2f`）、チャート名に「（円）」を追記

## デバイス・LP分析チャート
- LP別横棒チャートでY軸が空
  - **原因**: `adhoc_columns`が軸として認識されない
  - **解決**: BigQueryビューに`base_landing_page`列を追加し、`x_axis = "base_landing_page"`を直接指定
  - **実装**: `v_ga_sessions`に`REGEXP_EXTRACT(landing_page, r'^[^?]+')`列を追加
- URLパラメータが長すぎて見づらい
  - **原因**: `landing_page`列にクエリパラメータが含まれる
  - **解決**: `base_landing_page`列を使用（パラメータ除外済み）
  - **効果**: `https://winglish.site/?gad_source=...` → `https://winglish.site/`

## ファネル分析チャート
- 「Not enough segments」エラー（Chart作成失敗）
  - **原因**: Superset API経由でのFunnelチャートやTable chartの新規作成時に発生
  - **症状**: 
    - Chart 313（Funnel）、314（Table）の作成・再作成でエラー
    - Chart 315-318は正常動作（既存チャート）
    - Dataset 28、38どちらでも同じエラー
  - **考えられる原因**:
    - Supersetのバージョンや設定による制限
    - API経由での新規チャート作成にセキュリティ制限がかかっている
    - 特定のパラメータ（認証、権限など）が不足
  - **解決策**:
    - **UIから手動で作成**: Dashboard → "+" → "Create a new chart"
    - **既存チャートを複製**: Chart 315などの正常チャートを "Save as" で複製
    - **設定変更**: UIでGroupby、Metricsを調整
  - **回避策**:
    - API経由での新規作成を諦め、UI操作に切り替える
    - 既存チャートの更新（PUT）は正常動作するため、テンプレートチャートをUI作成→API更新で運用
  - **影響**: Chart 313は削除、Chart 314-318で代替分析可能
