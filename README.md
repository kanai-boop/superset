# プロジェクトREADME（運用の約束・参照）

## 目的（Purpose）
- Superset×BigQuery で安定してダッシュボードを構築・復旧できる土台を作る。
- 自然言語から自動でチャートを生成できる仕組みの基盤（API操作・テンプレ・契約）を整える。
- 作業と同時に仕様書へ反映し、再現性とチーム共有性を高める。

## 最終ゴール（Final Goals）
- 事故や環境変化時でも、Runbookの手順で短時間に完全復旧できる。
- 代表チャート（KPI・時系列・内訳・2軸・BigNumber）をテンプレから自動生成可能。
- データセット契約とAPI仕様が常に最新で、自然言語→API生成の精度が高い。
- 将来的には「プロンプトで表示項目をリアルタイムに作成・変更」できるSaaS機能の基盤とする。

## 運用ルール（仕様書更新ポリシー）
- 1チャートを「正しく表示」できたら、その場で仕様書に追記・更新。
- 追記先固定:
  - データ前提/計算列/メトリクス → `superset/docs/specs/dataset_contracts.md`
  - チャート params テンプレ → `superset/docs/specs/chart_templates.md`
  - コツ/落とし穴/API注意点 → `superset/docs/specs/superset_api_spec.md` または `superset/docs/specs/troubleshooting.md`
  - モデリング変更 → `superset/docs/specs/bigquery_modeling_spec.md`
- OpenAPI スナップショットは必要時に更新し、`superset/docs/specs/superset_openapi_<version>_<YYYY-MM-DD>.json` 命名で保存。

### Done の定義
- Explore でエラーなく可視化できる
- ダッシュボードで再実行OK（Time range フィルター連動）
- 上記いずれかの仕様書に必要記載を追加済み（可能ならチャートID/スクショ）

### 典型フロー（1チャート）
1. テンプレで作成→Explore実行→意図確認
2. 必要なら `dataset_contracts.md` に計算列/メトリクス追記
3. `chart_templates.md` に params を整形して追加
4. `troubleshooting.md` に注意点があれば追記
5. ダッシュボードに配置→Save

## 仕様書の読み順（推奨）

### 初回セットアップ・復旧時
1. **`docs/specs/restore_runbook.md`** - 環境構築・復旧手順（最優先）
2. **`docs/specs/bigquery_modeling_spec.md`** - BigQueryビュー定義とアクセス方法
3. **`docs/specs/dataset_contracts.md`** - データセット仕様（必須列・メトリクス）

### チャート作成時
1. **`docs/specs/chart_templates.md`** - チャートparamsテンプレート
2. **`docs/specs/superset_api_spec.md`** - API使用方法と注意点

### トラブル時
1. **`docs/specs/troubleshooting.md`** - 既知エラーと即時対処

### 高度な分析機能
1. **`docs/specs/master_dashboard_design.md`** - マスターダッシュボード（Executive Overview）
2. **`docs/specs/attribution_modeling_design.md`** - チャネルアトリビューション分析（Phase 1-4完了）
3. **`docs/specs/page_path_exploration_design.md`** - ページ経路分析
4. **`docs/specs/google_ads_dashboard_design.md`** - Google Ads パフォーマンス分析
5. **`docs/specs/device_landingpage_analysis_design.md`** - デバイス・LP分析
6. **`docs/specs/new_vs_returning_analysis_design.md`** - 新規 vs リピーター分析
7. **`docs/specs/time_pattern_analysis_design.md`** - 時間帯・曜日パターン分析
8. **`docs/specs/regional_analysis_design.md`** - 地域別パフォーマンス分析
9. **`docs/specs/content_performance_design.md`** - コンテンツパフォーマンス分析
10. **`docs/specs/channel_cross_analysis_design.md`** - チャネル × セグメント クロス分析
11. **`docs/specs/funnel_analysis_design.md`** - コンバージョンファネル分析

## その他参照
- OpenAPI スナップショット: `docs/specs/superset_openapi.json`
- 公式 API: https://superset.apache.org/docs/api

## 更新履歴
- 2025-10-31: 4指標×3期間のBigNumberを追加（Users/New Users/Sessions/CVR）。SQLベースの期間フィルターを`event_date`で適用、トレンド非表示・前期間比(Δ%)を有効化。`event_date`をTemporalに設定。仕様書（contracts/templates/troubleshooting）を更新。
- 2025-10-31（続）: PV（Pageviews）のビュー（`v_ga_page_views`）とデータセット（ID: 29→33に移行）を作成。BigNumberチャートで期間合計表示のため`aggregation: "sum"`と`granularity_sqla: "event_date"`の設定を明確化。MTDフィルターを年/月一致チェック方式に変更（タイムゾーン問題回避）。仕様書（chart_templates/dataset_contracts/bigquery_modeling/superset_api_spec/troubleshooting）を更新。
- 2025-11-01: 集客サマリダッシュボード（「アウトプット1」）を作成。カテゴリ別横棒チャート3つ（チャネル/メディア/参照元 TOP5、ID: 176-178）と時系列折れ線（Sessions vs Conversions 前月比較付き、ID: 175）を追加。`echarts_timeseries_bar`の`x_axis`にカテゴリ列を指定することで非時系列集計を実現。`time_compare: ["1 month ago"]`で前月比較を有効化。仕様書（chart_templates/troubleshooting）を更新。
- 2025-11-03: エンゲージメントレポート作成。`v_ga_sessions`にsession_pageviews列を追加（BigQuery）し、Total Pageviews/Pageviews per Session/Engagement Rate/Engaged Sessionsメトリクスを追加。6指標×3期間のBigNumber（ID: 179-196）、上位ページTOP10（ID: 197、base_url使用）、時系列2軸2つ（ID: 198-199、Query Bにもフィルター設定）を作成。`v_ga_page_views`にbase_url列を追加してURLパラメーター除外。仕様書（dataset_contracts/chart_templates/bigquery_modeling/troubleshooting）を更新。
- 2025-11-03（続）: 離脱率レポート作成。`v_ga_page_exits`ビュー（セッション最終ページを特定して離脱率計算）とデータセット（ID: 34）を作成。ページ別詳細テーブル（ID: 202）、時系列2軸（PV vs 離脱率、ID: 200）、バブルチャート（PV vs 離脱率、サイズ=離脱数、ID: 203）を作成。BigQueryへの直接アクセス方法（Python + google-cloud-bigquery）を仕様書に追記。仕様書（dataset_contracts/chart_templates/bigquery_modeling/troubleshooting/restore_runbook）を更新。
- 2025-11-10: アトリビューションパス分析実装（Phase 1-3完了）。`v_ga_attribution_paths`ビュー（コンバージョンまでのユーザージャーニーを追跡、Early/Middle/Lateタッチポイント分類）とデータセット（ID: 35）を作成。Phase 2: GA4スタイルのタッチポイント別貢献度チャート3つ（ID: 245-247）、パス集計テーブル（ID: 242）、タッチポイント数分布（ID: 244）を作成。Phase 3: 月別推移（ID: 248）、Sunburst階層可視化（ID: 249）、Chordチャネル遷移（ID: 250）、タッチポイントファネル（ID: 251）、チャネル別平均CV日数（ID: 252）を作成。ダッシュボード「アトリビューションパス分析（拡張版）」（ID: 17）に全10チャートを配置。コンバージョンイベントは`conversion_event_page_view`を使用（7,258 CV/月）。新規仕様書`attribution_modeling_design.md`を作成。
- 2025-11-10（続）: ページ経路分析実装（Phase 4完了）。GA4の「経路データ探索」機能を再現。`v_ga_page_paths`ビュー（CVまでのpage_viewイベントを時系列追跡、始点/終点/遷移を分析）とデータセット（ID: 36）を作成。始点ページTOP10（ID: 254）、終点ページTOP10（ID: 255）、ページ遷移テーブル（ID: 256）、ページ遷移Sunburst（ID: 257）の4チャートを作成。ダッシュボード「ページ経路分析（Path Exploration）」（ID: 18）を作成。データ規模: 始点83種類（6,500 CVs）、終点1,843種類（9,638 CVs）、遷移895パターン（3,761 CVs）。新規仕様書`page_path_exploration_design.md`を作成。
- 2025-11-10（続）: Google Ads パフォーマンスダッシュボード実装。既存の`v_ga_ads_performance`ビュー（Dataset ID: 27）を活用。KPI BigNumber 8つ作成（期間比較: ID 258-261,263,272 = 広告費/クリック/インプレッション/CV/CPC/CVR、全期間: ID 262,271 = ROAS/CPA）。10月データ（¥3,893、775クリック）vs 9月比較。時系列チャート4つ（ID: 264-267: 日別広告指標/日別CV・ROAS/CTR推移/月別テーブル）と分析チャート3つ（ID: 268-270: 広告効率Bubble/週別広告費/サマリー全期間）を作成。全金額を円表示（数値フォーマット`,d`/`,.2f`、チャート名に「（円）」追記）に統一。ダッシュボード「Google Ads パフォーマンス」（ID: 19）を作成。主要効率指標（CTR、CPC、ROAS、CPA、CVR）をアドホックメトリクスで定義。新規仕様書`google_ads_dashboard_design.md`を作成。仕様書（dataset_contracts/chart_templates/troubleshooting）を更新。
- 2025-11-10（続）: デバイス・ランディングページ分析実装。既存の`v_ga_sessions`（Dataset ID: 28）を活用。`v_ga_sessions`ビューに`base_landing_page`列を追加（URLパラメータ除外版）。デバイス分析4チャート（ID: 273-276: セッション数/直帰率/エンゲージメント時間/月別推移積み上げ棒）、ランディングページ分析4チャート（ID: 277-280: セッション数TOP10横棒/直帰率TOP10横棒/パフォーマンステーブルTOP20/エンゲージメントBubble）を作成。ダッシュボード「デバイス・ランディングページ分析」（ID: 20）を作成。データ洞察: Mobile 83.5%、Desktop高エンゲージ（22.2秒）、TOPページ97.8%集中、全体直帰率77-81%。直帰率定義（`session_pageviews = 1`）を実装。新規仕様書`device_landingpage_analysis_design.md`を作成。仕様書（dataset_contracts/bigquery_modeling/troubleshooting）を更新。
- 2025-11-10（続）: 新規 vs リピーター分析実装。既存の`v_ga_sessions`の`new_vs_returning`列を活用（Dataset ID: 28）。6チャート作成（ID: 281-286: 構成比円グラフ/比較テーブル/月別推移積み上げ/デバイス別構成積み上げ/エンゲージメント比較横棒/直帰率比較横棒）。ダッシュボード「新規 vs リピーターユーザー分析」（ID: 21）を作成。データ洞察: 新規74.7%（直帰率71.6%、CVR 104.4%）、リピーター25.3%（直帰率60.9%、CVR 123.3%）。リピーターは直帰率が10.7pt低く、CVRが18.9pt高い（ロイヤリティ効果）。新規の直帰率改善とリテンション施策強化を提案。新規仕様書`new_vs_returning_analysis_design.md`を作成。
- 2025-11-10（続）: 時間帯・曜日パターン分析実装。`v_ga_sessions`ビューに時間帯・曜日列を追加（`session_hour`, `day_of_week`, `day_of_week_num`, `weekday_weekend`をタイムスタンプから抽出）。6チャート作成（ID: 287-292: 曜日別セッション縦棒/時間帯別セッション折れ線/平日週末比較テーブル/曜日別エンゲージメント横棒/時間曜日マトリクステーブル/時間帯別CVR折れ線）。ダッシュボード「時間帯・曜日パターン分析」（ID: 22）を作成。データ洞察: ピークタイム平日12-13時（ランチタイム）、水曜最高エンゲージ（11.1秒）、平日70%優勢（エンゲージ9.4秒 vs 週末6.4秒、直帰率67.9% vs 71.1%）。コンテンツ配信・広告配信の最適タイミング特定。新規仕様書`time_pattern_analysis_design.md`を作成。
- 2025-11-10（続）: 地域別パフォーマンス分析実装。既存の`v_ga_sessions`の`geo_country`, `geo_region`列を活用（Dataset ID: 28）。6チャート作成（ID: 293-298: 都道府県別セッション横棒TOP15/都道府県別エンゲージメント横棒TOP15/都道府県別テーブルTOP20/国別セッション横棒TOP10/都道府県別BubbleエンゲージvsCV/主要地域月別推移折れ線TOP5）。ダッシュボード「地域別パフォーマンス分析」（ID: 23）を作成。データ洞察: 日本97.6%、東京14.9%（エンゲージ13.4秒、直帰率60.5%最良）、関東圏28%集中、高エンゲージ地域は首都圏（東京/埼玉12.9秒/神奈川11.1秒）。エリアマーケティング3層戦略（関東圏40%/主要都市30%/その他30%）を提案。新規仕様書`regional_analysis_design.md`を作成。
- 2025-11-10（続）: コンテンツパフォーマンス分析実装。`v_ga_content_performance`ビュー（page_viewイベントからページ別指標集計、エントリー/エグジット判定、CV関連付け）とデータセット（ID: 37）を作成。7チャート作成（ID: 299-305: 人気コンテンツランキング横棒TOP15/エンゲージ高いコンテンツ横棒TOP15/パフォーマンステーブルTOP30/CV貢献度横棒TOP15/パフォーマンスBubbleエンゲージvsCVR/月別トレンド折れ線TOP5/エントリーエグジットテーブルTOP20）。ダッシュボード「コンテンツパフォーマンス分析」（ID: 24）を作成。データ洞察: TOPページ圧倒的（16,382 PV, CVR 90.8%, エンゲージ12.3秒）、学習コンテンツはエンゲージ0秒（瞬間離脱）、Login高CVR（98.8%）。TOPページ最適化優先、学習コンテンツ充実化、エグジット対策（CTA追加）を提案。新規仕様書`content_performance_design.md`を作成。
- 2025-11-10（続）: チャネル × セグメント クロス分析実装。既存の`v_ga_sessions`（Dataset ID: 28）を活用。7チャート作成（ID: 306-312: チャネル×デバイス構成積み上げTOP10/チャネル×デバイス詳細テーブルTOP30/チャネル×地域テーブルTOP50/チャネル×時間帯折れ線主要5チャネル/チャネル×新規リピーター積み上げTOP10/チャネル×新規リピーター詳細テーブルTOP30/チャネル×曜日テーブルTOP50）。ダッシュボード「チャネル × セグメント クロス分析」（ID: 25）を作成。データ洞察: Google Ads mobile 86.5%（直帰率86.8%）、desktop高品質（直帰率62.5%、エンゲージ13.5秒）、新規97.2%（リピーター2.8%だがエンゲージ1.8倍）、12-13時ピーク（1,263セッション）、日曜月曜ピーク水曜谷（35%差）。時間帯・曜日別入札調整、モバイルUX改善、デスクトップ詳細コンテンツ、新規獲得とリテンション分離戦略を提案。新規仕様書`channel_cross_analysis_design.md`を作成。
- 2025-11-11: コンバージョンファネル分析実装。`v_ga_funnel_analysis`ビュー（5ステップファネル: ランディング/エンゲージPV>=2/閲覧継続10秒以上/アクションPV>=3/CV）とデータセット（ID: 38）を作成。5チャート作成（ID: 314-318: ファネル詳細テーブル/デバイス別ファネル比較/チャネル別ファネル効率TOP20/新規vsリピーターファネル/デバイス別離脱率）。ダッシュボード「コンバージョンファネル分析」（ID: 26）を作成。Chart 313（Funnel全体）はSuperset API制限（"Not enough segments"エラー）により削除、Chart 314-318で代替分析可能。データ洞察: 直帰率69.4%が最大のボトルネック（Step1→2）、最終CVR 84.6%と高い、Google Adsエンゲージ16.0%低いがCVR 91.5%高い（質より量）、Organicエンゲージ43.3%高いがCVR 41.6%（探索型）、Tablet CVR 88.8%最高。LP最適化優先、チャネル別戦略（Ads簡潔化/Organic教育型）、デバイス最適化を提案。新規仕様書`funnel_analysis_design.md`を作成。トラブルシューティングに「Not enough segments」エラー対処を追記。
- 2025-11-11（続）: マスターダッシュボード設計書作成。経営層向けの総合ダッシュボード「マスターダッシュボード（Executive Overview）」（Dashboard 27予定）の仕様を策定。12チャート設計（ID: 319-330: KPI BigNumber 6種10月vs9月比較/セッションCV推移30日/チャネル別構成積み上げ/デバイス構成円グラフ/地域TOP5テーブル/ファネル簡易版/月次KPIサマリー3ヶ月）。主要洞察: CVRが100%超え（異常値、CVイベント定義見直し必要）、直帰率70%（LP最適化必要）、9月ピーク（原因調査必要）。Superset API制限により**UIから手動作成が必須**（既存チャート複製推奨）。詳細な手動作成手順を記載。毎朝のチェックリスト、異常検知時のアクション、深掘り分析への導線（専門ダッシュボード8種）を整備。新規仕様書`master_dashboard_design.md`を作成。
- 2025-11-12: Google Ads 指標詳細分析チャート追加。既存ビュー`v_ga_ads_performance`（Dataset ID: 27）を活用し、日別指標の相関を可視化する4チャート（ID: 321-324）をAPI経由で作成：コスト vs CTR バブルチャート、日別詳細テーブル、日別広告費×CV×ROAS複合チャート、CPC推移（90日）。DevToolsで取得した`params`/`query_context`ペイロードを再現し、`Authorization: Bearer` + `X-CSRFToken` のヘッダー構成で自動生成が成功。`chart_templates.md`と`google_ads_dashboard_design.md`にテンプレートと手順を更新し、レイアウト配置ガイドを追記。
