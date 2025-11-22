# マルチテナントSaaS 展開計画（Superset + BigQuery + croudrun）

本ドキュメントは、開発環境で構築した Superset + BigQuery の分析基盤を、マルチテナント SaaS として提供するための方針をまとめる。

## 0. ゴールと前提
- croudrun 上に Superset をホスティングし、複数顧客（テナント）へ分析ダッシュボードを提供する。
- BigQuery 上の顧客データを安全に接続し、顧客ごとのアクセス制御を徹底する。
- 後続で自然言語チャットからチャート生成できる機能を組み込む。

---

## 1. アーキテクチャ方針

### 1-1. 分離アプローチ
| フェーズ | 構成 | メリット | 留意点 |
| --- | --- | --- | --- |
| フェーズ1 | **単一 Superset インスタンス** 内で論理マルチテナント | 運用がシンプル・テンプレ展開が容易 | ロール設計・RLSで分離徹底 | 
| フェーズ2 (必要時) | テナントごとに Superset インスタンスを複製 | セキュリティ・カスタマイズ柔軟性 | デプロイ/運用コスト増 |

### 1-2. 構成要素
- Superset Web (Gunicorn)、Superset Celery Worker（必要に応じて）
- Superset metadata DB (Postgres)
- Redis (cache)
- BigQuery (各顧客データ)
- Ingress/HTTPS (croudrun)

### 1-3. 展開フロー
1. GitHub にてアプリ・インフラコード管理
2. CI/CD (Lint/Test → Docker Build → croudrun Deploy)
3. Config/Secrets を croudrun Secret Store で管理（Superset SECRET_KEY、SAキー等）
4. 環境：`dev` → `stg` → `prod`

---

## 2. テナント管理モデル

### 2-1. 認証・認可
- 初期は Superset 内蔵 Auth(DB) を利用。テナント別ロール（例: `customer_a_admin`, `customer_a_viewer`）。
- `CUSTOM_SECURITY_MANAGER` を拡張し、ユーザー作成時のロール付与や RLS ルールを自動化。
- 将来的な SSO (Google, AzureAD 等) に備え、OAuth 設定を `superset_config.py` でパラメータ化。

### 2-2. 権限・データセット
- 顧客ごとに Superset Database 接続を作成 (BigQuery への接続文字列)。
- Dataset は顧客専用に作成し、ロールに `database_access` / `dataset_access` を付与。
- 共有テンプレート JSON からダッシュボードを複製し、顧客専用 ID に紐付け。

### 2-3. BigQuery 側の分離
- 推奨: 顧客ごとに BigQuery プロジェクト or データセットを分け、専用サービスアカウントで接続。
- 共有プロジェクトの場合は View + Row Level Security で論理分離し、Superset 側でも RLS を設定。

### 2-4. メタデータ管理
- `tenants` テーブル（顧客名、BQ情報、SupersetロールID、ダッシュボードID等）をPostgresに作成。
- オンボーディング CLI で Database/Dataset/Role/User/Dashboard を一括生成。

---

## 3. デプロイ／運用（croudrun）

1. **リポジトリ構成例**
   - `superset/`：アプリ（Dockerfile、`superset_config.py`、fixtures、プラグイン）
   - `infra/`：croudrun マニフェスト (YAML or Terraform)
   - `scripts/`：`provision_tenant.py`, `import_dashboards.py` など
2. **CI/CD**
   - GitHub Actions → lint/test → Docker build (`superset_app`, `superset_worker`) → croudrun deploy
3. **Secrets**
   - Superset `SECRET_KEY`
   - BigQuery サービスアカウント (テナント分)
   - OAuth クライアント情報 (将来導入)
4. **バックアップ**
   - Superset metadata DB: daily snapshot
   - Dashboards: `superset export-dashboards` を定期実行
5. **スケーリング**
   - Web Pod Horizontal Scaling + Redis セッション共有
   - Celery Worker 追加で重データ処理を隔離

---

## 4. アプリケーション差異化 & オンボーディング

### 4-1. ブランド/UI の切り替え
- `superset_config.py` で `APP_NAME`, `LOGO_ICON` をテナント context に応じて差し替える。
- ログイン後、Flask `before_request` でテナント情報を判定し `g.tenant` に格納。

### 4-2. テンプレート展開
- 仕様書にあるテンプレ JSON (`docs/specs/chart_templates.md`, 各ダッシュボード設計書) をテンプレとして import。
- テナント追加時にチャートID/DatasetID を差し替える CLI を実装。

### 4-3. アクセス制御
- Explore/SQL Lab の表示有無をロールごとに制御。
- Feature Flags (例: `ALLOW_DASHBOARD_DOMAIN_SHARDING`) をテナントで切替。

### 4-4. オンボーディングフロー
1. 管理画面/CLIからテナント基本情報と BigQuery 接続 JSON を登録
2. CLI で Database/Dataset/Dashboard を自動生成（権限付与含む）
3. 初回ログイン時に「Getting Started Dashboard」を表示し、使い方をガイド

---

## 5. 非機能要件

### 5-1. 監視・ログ
- Superset のアクセスログ、SQLログを外部集約（BigQuery or Stackdriver）。
- `Prometheus` 連携で Pod 指標、SQL ファイル数、エラー率を可視化。
- BigQuery Billing Export を有効化し、クエリコストをテナント別に集計。

### 5-2. セキュリティ
- HTTPS + WAF。Superset ←→ BigQuery は Private Service Connect などで閉域化。
- Superset DB Auth + MFA。SSO 導入時は OAuth/SAML を検討。
- RLS/権限に加え、BigQuery IAMでテナント毎に SA を分離。

### 5-3. 可用性 / DR
- metadata DB の冗長化、定期バックアップ。
- Dashboards の Git コントロールと export 自動化。
- DR 手順を Runbook 化（別リージョン再構築方法）。

### 5-4. 課金・コスト管理
- 利用メトリクス（ログイン数、ダッシュボード閲覧）と BigQuery bytes processed をテナント別に記録。
- 課金モデル案：
  - 基本料金＋BigQueryクエリコスト実費
  - あるいはユーザー数ベース＋クエリコスト閾値超過分を追加請求
- Billing Export + Looker Studio / Superset で管理者向けコストダッシュボードを提供。

---

## 6. 自然言語チャート生成チャット

### 6-1. 処理フロー（概要）
1. ユーザーがチャットUIで意図を入力
2. LLM がテンプレート候補とパラメータ（データセット、メトリクス、期間等）を出力
3. バックエンドで Superset API `POST /api/v1/chart/` を呼び、チャートを生成
4. 完成したチャートの Explore URL / Dashboard をユーザーに返す

### 6-2. LLM 選定と方針
- **フェーズ1**：マネージド LLM API（OpenAI/Azure/Vertex）で PoC。スピード重視。
- **フェーズ2**：利用パターンを見て Vertex AI で OSS モデル (Llama/Mixtral) をホスト。必要に応じて自前 GPU 推論も検討。

### 6-3. アーキテクチャ
- `chat-service` (FastAPI 等) を croudrun に配置。テナント情報を参照し、コール時に権限を反映。
- LLM へ渡すプロンプトには、チャートテンプレ/データセット契約情報を few-shot 提供。
- サーバーサイドでテンプレを検証するため、LLM には「どのテンプレートを使うか」「各パラメータは何か」を回答させるだけにし、最終的な JSON 組み立てはアプリ側が実施。

### 6-4. 品質と安全性
- 生成結果を Superset API に送る前にスキーマバリデーション。
- 失敗ケースはログ化し、人手レビュー → テンプレートを改善し few-shot に追加。
- テナントIDごとの許可データセット一覧を参照し、LLM が他テナントのリソースを提案しないよう制御。

---

## 7. 今後のタスク候補
1. croudrun 上で Superset を PoC デプロイ
2. テナント自動プロビジョン CLI の実装
3. ログ/監視基盤の整備（Prometheus + BigQuery Audit）
4. LLM チャット PoC（マネージド API で単一テンプレ生成）
5. 課金レポート用ダッシュボード作成

---

## 参考資料
- `docs/specs/google_ads_dashboard_design.md` – 既存テンプレート
- `docs/specs/chart_templates.md` – チャート JSON テンプレ一覧
- `docs/specs/dataset_contracts.md` – BigQuery View / Dataset 契約
- Superset 公式: [Security](https://superset.apache.org/docs/security/) / [API](https://superset.apache.org/docs/api)
