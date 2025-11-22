# Cursor 運用ルール（仕様書更新ポリシー）

## 目的
小さく確実に積み上げるため、チャートやデータセットを実装したら即ドキュメント化する運用を徹底する。

## 基本ルール
- 1チャートを「正しく表示」できたら、その場で仕様書に追記・更新する。
- 追記先は固定:
  - データ前提/計算列/メトリクス → `superset/docs/specs/dataset_contracts.md`
  - チャートの params テンプレ → `superset/docs/specs/chart_templates.md`
  - コツ/落とし穴/API注意点 → `superset/docs/specs/superset_api_spec.md` または `superset/docs/specs/troubleshooting.md`
  - データモデリング変更時 → `superset/docs/specs/bigquery_modeling_spec.md`
- OpenAPI スナップショットは必要時に更新し、`superset/docs/specs/superset_openapi_<version>_<YYYY-MM-DD>.json` 命名で保存。

## Done の定義（受け入れ基準）
- Explore でエラーなく意図どおりに表示できる。
- ダッシュボードに配置して再実行OK（Time range フィルター連動）。
- 上記いずれかの仕様書に必要記載を追加済み（可能ならチャートID/スクショ）。

## 追加ルール
- 既存テンプレを流用し、差分だけ記録（重複テンプレを作らない）。
- 新規メトリクスはまず `dataset_contracts.md` に記載→API反映→チャート適用。
- エラーに遭遇したら、再現条件＋一発解決コマンドを `troubleshooting.md` に追記。

## 典型フロー（1チャート）
1. テンプレで作成→Explore 実行→意図確認。
2. 必要なら `dataset_contracts.md` に計算列/メトリクスを追記（実式付き）。
3. `chart_templates.md` に params を整形して追加（`datasource` は `<DATASET_ID>__table`）。
4. `troubleshooting.md` に注意点があれば追記。
5. ダッシュボードに配置→Save。

## 参照
- 実務向け API 仕様: `superset/docs/specs/superset_api_spec.md`
- 公式 API ドキュメント: https://superset.apache.org/docs/api
