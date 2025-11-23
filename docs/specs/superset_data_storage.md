# Superset データ保存場所と構造

## 概要
Supersetのチャートやダッシュボードは、**メタデータデータベース（PostgreSQL/MySQL等）**に保存されます。データベースが消えると、作成したチャート・ダッシュボードも全て失われます。

---

## 1. データベースの場所

### Docker Compose環境の場合
- **データベースコンテナ**: `superset_db` (PostgreSQL 16)
- **データ保存場所**: Docker Volume `superset_db_home`
  - 物理的な場所: Dockerが管理するボリューム（通常は `/var/lib/docker/volumes/superset_db_home/`）
  - **重要**: このボリュームが削除されると、全てのチャート・ダッシュボードが失われます

### Cloud Run環境の場合
- **データベース**: **外部PostgreSQLサービス**（必須）
  - **重要**: Cloud Runはステートレスなため、Docker Volumeは使えません
  - データベースは必ず外部サービスとして管理する必要があります
- **選択肢**:
  1. **Cloud SQL for PostgreSQL**（GCP統合、推奨）
  2. **Supabase**（無料枠あり、開発環境向け）
  3. **Neon**（Serverless、無料枠あり）
  4. **Render.com**（簡単セットアップ）
  5. **その他の外部PostgreSQL**（VPS、他のクラウドなど）
- **接続方法**: 
  - パブリックIP + SSL接続（一般的）
  - Cloud SQL Proxy経由（Cloud SQL使用時のみ）
- **バックアップ**: サービス提供元の自動バックアップ機能を使用、または手動設定

#### ⚠️ Cloud SQLの料金について
- **Cloud SQLは有料サービス**です（無料枠は限定的）
- **料金例**（東京リージョン、Enterprise Edition）:
  - vCPU 2コア、メモリ7.5 GiB、ストレージ100 GiB: 約$153/月（約23,000円/月）
  - 最小構成（db-f1-micro）でも約$7-10/月程度
- **無料トライアル**: Google Cloudの無料トライアル（$300クレジット、90日間）で試用可能
- **代替案**: 
  - **開発環境**: Cloud SQLの最小構成、または外部PostgreSQL（Render.com、Supabase無料枠など）
  - **本番環境**: Cloud SQLが推奨（自動バックアップ、高可用性、セキュリティ）

### 確認方法

#### Docker Compose環境
```bash
# ボリューム一覧を確認
docker volume ls | grep db

# ボリュームの詳細情報（マウントポイントなど）
docker volume inspect superset_db_home
```

#### Cloud Run環境
```bash
# Cloud SQLインスタンス一覧
gcloud sql instances list

# Cloud SQLインスタンスの詳細
gcloud sql instances describe <INSTANCE_NAME>

# Cloud Runサービスから接続確認
gcloud run services describe <SERVICE_NAME> --region=<REGION>
```

---

## 2. 保存されているテーブル

### 主要テーブル

#### `slices` テーブル（チャート）
- **役割**: チャート（ビジュアライゼーション）の定義を保存
- **主要カラム**:
  - `id`: チャートID（例: 258, 259, 321...）
  - `slice_name`: チャート名
  - `viz_type`: チャートタイプ（`big_number`, `table`, `bubble` など）
  - `datasource_id`: データセットID
  - `datasource_type`: データセットタイプ（`table` など）
  - `params`: チャート設定（JSON文字列）
  - `query_context`: クエリコンテキスト（JSON文字列）
  - `created_on`, `changed_on`: 作成・更新日時

#### `dashboards` テーブル（ダッシュボード）
- **役割**: ダッシュボードの定義を保存
- **主要カラム**:
  - `id`: ダッシュボードID（例: 19, 20, 26...）
  - `dashboard_title`: ダッシュボード名
  - `position_json`: チャートの配置情報（JSON）
  - `json_metadata`: ダッシュボードのメタデータ（JSON）
  - `slug`: URL用のスラッグ
  - `published`: 公開フラグ
  - `created_on`, `changed_on`: 作成・更新日時

#### `dashboard_slices` テーブル（関連テーブル）
- **役割**: ダッシュボードとチャートの関連を保存
- **主要カラム**:
  - `dashboard_id`: ダッシュボードID
  - `slice_id`: チャートID

#### その他の重要テーブル
- `dbs`: データベース接続情報（BigQuery接続など）
- `tables`: データセット（Dataset）情報
- `ab_user`: ユーザー情報
- `ab_role`: ロール情報
- `ab_permission`: 権限情報

---

## 3. データの確認方法

### 方法1: Superset API経由
```bash
# チャート一覧
curl -H "Authorization: Bearer $TOKEN" \
  https://your-superset/api/v1/chart/

# ダッシュボード一覧
curl -H "Authorization: Bearer $TOKEN" \
  https://your-superset/api/v1/dashboard/

# 特定チャートの詳細
curl -H "Authorization: Bearer $TOKEN" \
  https://your-superset/api/v1/chart/258
```

### 方法2: PostgreSQLに直接接続
```bash
# Docker Compose環境の場合
docker compose exec db psql -U superset -d superset

# チャート一覧を確認
SELECT id, slice_name, viz_type, datasource_id 
FROM slices 
ORDER BY id DESC 
LIMIT 10;

# ダッシュボード一覧を確認
SELECT id, dashboard_title, published, changed_on 
FROM dashboards 
ORDER BY id DESC 
LIMIT 10;

# 特定ダッシュボードに含まれるチャート
SELECT d.dashboard_title, s.slice_name, s.id as chart_id
FROM dashboards d
JOIN dashboard_slices ds ON d.id = ds.dashboard_id
JOIN slices s ON ds.slice_id = s.id
WHERE d.id = 19;
```

---

## 4. データのバックアップ方法

### 方法1: PostgreSQLダンプ（推奨）

#### Docker Compose環境
```bash
# データベース全体をダンプ
docker compose exec db pg_dump -U superset superset > superset_backup_$(date +%Y%m%d).sql

# 特定テーブルのみダンプ
docker compose exec db pg_dump -U superset -t slices -t dashboards -t dashboard_slices superset > charts_backup.sql
```

#### Cloud Run環境（Cloud SQL）
```bash
# Cloud SQL Proxy経由でダンプ
cloud-sql-proxy <PROJECT_ID>:<REGION>:<INSTANCE_NAME> &
pg_dump -h 127.0.0.1 -U superset -d superset > superset_backup_$(date +%Y%m%d).sql

# または、gcloudコマンドで直接ダンプ
gcloud sql export sql <INSTANCE_NAME> \
  gs://<BUCKET_NAME>/superset_backup_$(date +%Y%m%d).sql \
  --database=superset

# Cloud SQLの自動バックアップを有効化（推奨）
gcloud sql instances patch <INSTANCE_NAME> \
  --backup-start-time=03:00 \
  --enable-bin-log
```

### 方法2: Superset Export API
```bash
# チャートをJSONでエクスポート
curl -H "Authorization: Bearer $TOKEN" \
  https://your-superset/api/v1/chart/export/?q=\(ids:!\(258,259,321\)\) \
  > charts_export.json

# ダッシュボードをJSONでエクスポート
curl -H "Authorization: Bearer $TOKEN" \
  https://your-superset/api/v1/dashboard/export/?q=\(ids:!\(19,20,26\)\) \
  > dashboards_export.json
```

### 方法3: Docker Volumeのバックアップ
```bash
# ボリューム全体をバックアップ
docker run --rm \
  -v superset_db_home:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/db_volume_backup_$(date +%Y%m%d).tar.gz /data
```

---

## 5. データの復元方法

### 方法1: PostgreSQLダンプから復元

#### Docker Compose環境
```bash
# ダンプファイルから復元
docker compose exec -T db psql -U superset superset < superset_backup_20250101.sql
```

#### Cloud Run環境（Cloud SQL）
```bash
# Cloud SQL Proxy経由で復元
cloud-sql-proxy <PROJECT_ID>:<REGION>:<INSTANCE_NAME> &
psql -h 127.0.0.1 -U superset -d superset < superset_backup_20250101.sql

# または、GCSから直接インポート
gcloud sql import sql <INSTANCE_NAME> \
  gs://<BUCKET_NAME>/superset_backup_20250101.sql \
  --database=superset

# Cloud SQLの自動バックアップから復元（ポイントインタイムリカバリ）
gcloud sql backups restore <BACKUP_ID> \
  --backup-instance=<INSTANCE_NAME> \
  --restore-instance=<INSTANCE_NAME>
```

### 方法2: Superset Import API
```bash
# JSONファイルからインポート
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @charts_export.json \
  https://your-superset/api/v1/chart/import/
```

### 方法3: Docker Volumeから復元
```bash
# ボリュームを復元
docker run --rm \
  -v superset_db_home:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/db_volume_backup_20250101.tar.gz -C /
```

---

## 6. データが消えた原因の特定

### よくある原因
1. **Docker Volumeの削除**
   ```bash
   # 危険: これで全て消える
   docker volume rm superset_db_home
   ```
2. **データベースコンテナの再作成**
   - `docker compose down -v` を実行するとボリュームも削除される
3. **データベースの初期化**
   - `superset db upgrade` を間違って実行した場合
4. **手動でのテーブル削除**
   - 直接SQLで `DELETE FROM slices` などを実行した場合

### 確認方法
```bash
# データベースのテーブル一覧を確認
docker compose exec db psql -U superset -d superset -c "\dt"

# チャート数・ダッシュボード数を確認
docker compose exec db psql -U superset -d superset -c \
  "SELECT COUNT(*) as chart_count FROM slices;"
docker compose exec db psql -U superset -d superset -c \
  "SELECT COUNT(*) as dashboard_count FROM dashboards;"
```

---

## 7. マルチテナントSaaSでの考慮事項

### データ分離
- **テナントごとのデータ**: `slices` や `dashboards` テーブルに `tenant_id` カラムを追加するか、別テーブルで管理
- **推奨**: テナントごとにSupersetインスタンスを分ける（アプローチB）か、RLS（Row Level Security）で論理分離

### バックアップ戦略

#### Docker Compose環境
- **テナントごとのバックアップ**: テナントIDでフィルタしてエクスポート
- **定期バックアップ**: 日次でPostgreSQLダンプを取得し、S3/GCSに保存
- **ポイントインタイムリカバリ**: PostgreSQLのWAL（Write-Ahead Logging）を有効化

#### Cloud Run環境（Cloud SQL）
- **Cloud SQL自動バックアップ**: 日次自動バックアップを有効化（推奨）
  ```bash
  gcloud sql instances patch <INSTANCE_NAME> \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --retained-backups-count=7
  ```
- **GCSへの定期エクスポート**: Cloud Scheduler + Cloud Functionsで自動化
  ```bash
  # Cloud Schedulerで定期実行
  gcloud scheduler jobs create http export-superset-db \
    --schedule="0 3 * * *" \
    --uri="https://<REGION>-<PROJECT_ID>.cloudfunctions.net/export-db" \
    --http-method=POST
  ```
- **ポイントインタイムリカバリ**: Cloud SQLの自動バックアップから任意の時点に復元可能

### データ移行
- **テナント追加時**: テンプレートJSONから `import` APIで一括作成
- **テナント削除時**: 該当テナントのチャート・ダッシュボードを削除（`DELETE` API or SQL）

### Cloud Run環境での注意点
1. **ステートレス**: Cloud Runコンテナは再起動時に消えるため、データは必ずCloud SQLに保存
2. **接続プール**: Cloud SQL Proxyを使用し、接続プールを適切に設定
3. **スケーリング**: 複数インスタンス間でセッション共有が必要な場合はRedisを使用
4. **コスト**: Cloud SQLインスタンスのサイズとバックアップ保持期間でコストが変動

### Cloud Run環境でのPostgreSQL選択肢比較

| サービス | 無料枠 | 有料料金 | メリット | デメリット | 推奨用途 |
|---------|--------|---------|---------|-----------|---------|
| **Cloud SQL** | なし（$300トライアルのみ） | $7-150/月 | GCP統合、自動バックアップ、高可用性 | 料金が高い | 本番環境 |
| **Supabase** | 500MB、2時間バックアップ | $25/月から | 無料枠あり、簡単セットアップ | 無料枠は制限あり | 開発・PoC |
| **Neon** | 0.5GB、自動スケーリング | $19/月から | サーバーレス、ブランチ機能 | 無料枠は制限あり | 開発・PoC |
| **Render.com** | 90日トライアル | $7/月から | 簡単デプロイ、自動バックアップ | トライアル期間のみ | 開発・PoC |
| **Railway** | $5クレジット/月 | 使用量ベース | 簡単デプロイ、GitHub連携 | 無料枠は少ない | 開発・PoC |

#### 詳細

1. **Supabase（PostgreSQL）**
   - 無料枠: 500MBストレージ、2時間自動バックアップ
   - 料金: 無料枠あり、有料プランは$25/月から
   - メリット: 簡単セットアップ、自動バックアップ、REST API付き
   - 接続: パブリックIP + SSL接続

2. **Neon（Serverless PostgreSQL）**
   - 無料枠: 0.5GBストレージ、自動スケーリング
   - 料金: 無料枠あり、有料プランは$19/月から
   - メリット: サーバーレス、自動スケーリング、ブランチ機能
   - 接続: パブリックIP + SSL接続

3. **Render.com（PostgreSQL）**
   - 無料枠: 90日間の無料トライアル
   - 料金: 有料プランは$7/月から
   - メリット: 簡単デプロイ、自動バックアップ
   - 接続: パブリックIP + SSL接続

4. **Railway（PostgreSQL）**
   - 無料枠: $5クレジット/月
   - 料金: 使用量ベース
   - メリット: 簡単デプロイ、GitHub連携
   - 接続: パブリックIP + SSL接続

5. **Cloud SQL for PostgreSQL**（本番環境向け）
   - 無料枠: なし（$300トライアルのみ）
   - 料金: 最小構成で約$7-10/月、標準構成で約$50-150/月
   - メリット: GCP統合、マネージドサービス、スケーラビリティ、自動バックアップ
   - 接続: Cloud SQL Proxy経由（推奨）またはパブリックIP + SSL

#### コスト最適化のヒント
1. **開発環境**: Supabase無料枠やNeon無料枠を活用
2. **ステージング環境**: Cloud SQLの最小構成（db-f1-micro）
3. **本番環境**: 必要に応じてCloud SQLの標準構成を使用
4. **バックアップ**: 自動バックアップの保持期間を調整（7日→3日など）

---

## 9. 将来性を考慮した選択指針（マルチテナントSaaS向け）

### 9-1. 評価軸

| 評価項目 | 説明 | 重要度 |
|---------|------|--------|
| **スケーラビリティ** | テナント数増加に対応できるか | ⭐⭐⭐⭐⭐ |
| **コスト効率** | テナント数に応じたコスト増加が適切か | ⭐⭐⭐⭐ |
| **パフォーマンス** | 複数テナント同時アクセス時の性能 | ⭐⭐⭐⭐⭐ |
| **セキュリティ** | 企業向けSaaSとしての信頼性 | ⭐⭐⭐⭐⭐ |
| **運用性** | 自動バックアップ、監視、アラート | ⭐⭐⭐⭐ |
| **統合性** | GCP（Cloud Run + BigQuery）との統合 | ⭐⭐⭐⭐ |
| **ロックイン** | ベンダーロックインのリスク | ⭐⭐⭐ |
| **移行性** | 将来的な移行のしやすさ | ⭐⭐⭐ |

### 9-2. サービス別評価（将来性）

#### 🏆 Cloud SQL for PostgreSQL（最推奨）

**評価: ⭐⭐⭐⭐⭐**

**メリット:**
- ✅ **GCP統合**: Cloud Run、BigQuery、IAM、VPCと完全統合
- ✅ **スケーラビリティ**: テナント数増加に柔軟に対応（自動スケーリング可能）
- ✅ **高可用性**: マルチゾーン構成、自動フェイルオーバー
- ✅ **セキュリティ**: VPC内接続、IAM統合、暗号化
- ✅ **運用性**: 自動バックアップ、ポイントインタイムリカバリ、監視統合
- ✅ **パフォーマンス**: 専用インスタンス、接続プール最適化
- ✅ **コンプライアンス**: SOC2、ISO27001等の認証取得

**デメリット:**
- ❌ 料金が高い（最小構成で$7-10/月、標準構成で$50-150/月）
- ❌ GCPロックイン（ただし、PostgreSQL標準なので移行は可能）

**推奨シナリオ:**
- 本番環境（特に企業向けSaaS）
- テナント数が10社以上になる見込み
- セキュリティ・コンプライアンス要件が厳しい場合

---

#### 🥈 Supabase（開発・小規模向け）

**評価: ⭐⭐⭐**

**メリット:**
- ✅ 無料枠あり（開発・PoCに最適）
- ✅ セットアップが簡単
- ✅ REST API、リアルタイム機能付き
- ✅ オープンソース（ロックインリスク低）

**デメリット:**
- ❌ 無料枠は制限あり（500MB、2時間バックアップ）
- ❌ スケーラビリティに限界（大規模テナントには不向き）
- ❌ GCP統合が弱い（外部サービス）
- ❌ パフォーマンス保証が限定的

**推奨シナリオ:**
- 開発環境・PoC
- テナント数が5社未満の小規模運用
- コストを最小限に抑えたい場合

---

#### 🥉 Neon（サーバーレス向け）

**評価: ⭐⭐⭐**

**メリット:**
- ✅ サーバーレス（自動スケーリング）
- ✅ 無料枠あり（0.5GB）
- ✅ ブランチ機能（開発環境の分離に便利）
- ✅ オープンソース（ロックインリスク低）

**デメリット:**
- ❌ 無料枠は制限あり
- ❌ GCP統合が弱い
- ❌ 大規模運用の実績が少ない
- ❌ コスト予測が難しい（使用量ベース）

**推奨シナリオ:**
- 開発環境（ブランチ機能を活用）
- 小規模本番環境
- サーバーレスアーキテクチャを採用している場合

---

### 9-3. 段階的アプローチ（推奨戦略）

#### フェーズ1: 開発・PoC（0-3ヶ月）
- **選択**: **Supabase無料枠**
- **理由**: コスト0、セットアップ簡単、機能検証に十分
- **移行準備**: Cloud SQLへの移行手順を事前に検証

#### フェーズ2: 初期本番（3-12ヶ月、テナント1-10社）
- **選択**: **Cloud SQL最小構成（db-f1-micro）**
- **理由**: GCP統合、自動バックアップ、セキュリティ、コスト$7-10/月
- **監視**: Cloud Monitoringでパフォーマンス・コストを監視

#### フェーズ3: スケール時（12ヶ月以降、テナント10社以上）
- **選択**: **Cloud SQL標準構成（db-n1-standard-1以上）**
- **理由**: パフォーマンス、高可用性、スケーラビリティ
- **最適化**: 接続プール、読み取りレプリカ、キャッシュ戦略

#### フェーズ4: 大規模（テナント50社以上）
- **選択**: **Cloud SQL高可用性構成 + 読み取りレプリカ**
- **理由**: マルチゾーン、自動フェイルオーバー、負荷分散
- **追加**: Redisキャッシュ、CDN、クエリ最適化

---

### 9-4. 最終推奨

**マルチテナントSaaSとして展開する場合:**

1. **短期（開発・PoC）**: Supabase無料枠で開始
2. **中期（本番初期）**: Cloud SQL最小構成に移行
3. **長期（スケール時）**: Cloud SQL標準構成にスケールアップ

**理由:**
- GCP（Cloud Run + BigQuery）を使っているため、Cloud SQLとの統合が最適
- テナント数増加に柔軟に対応できるスケーラビリティ
- 企業向けSaaSとして必要なセキュリティ・コンプライアンス要件を満たせる
- 自動バックアップ、監視、アラートなどの運用機能が充実
- PostgreSQL標準なので、将来的に移行が必要になっても対応可能

**コスト試算（年間）:**
- 開発環境（Supabase無料枠）: $0
- 本番環境（Cloud SQL最小構成）: $84-120/年（$7-10/月）
- 本番環境（Cloud SQL標準構成）: $600-1,800/年（$50-150/月）
- テナント1社あたりのコスト: $0.7-15/月（テナント数に応じて変動）

---

## 10. データ量の推定（10クライアントの場合）

### ⚠️ 重要な前提

**SupersetのPostgreSQLに保存されるのは「メタデータ」のみです。**

- ✅ **保存されるもの**: チャート定義、ダッシュボード定義、ユーザー情報、権限設定など
- ❌ **保存されないもの**: 実際のビジネスデータ（これはBigQueryに保存）

**つまり、クライアント数が増えても、実際のデータ量は増えません。**
- 増えるのは: チャート・ダッシュボードの定義（JSON）
- 増えないのは: 実際のデータ（BigQueryに保存されているため）

### 10-1. 現在のデータ量（参考値）

**開発環境（1クライアント相当）:**
- データベースサイズ: 約7.5MB
- チャート数: 約50-100個
- ダッシュボード数: 約10-20個
- ユーザー数: 1-5人

### 10-2. Supersetメタデータの内訳

| データ種別 | 1クライアントあたり | 10クライアント（推定） |
|-----------|-------------------|---------------------|
| **チャート（slices）** | 50-100個 | 500-1,000個 |
| **ダッシュボード（dashboards）** | 10-20個 | 100-200個 |
| **ユーザー（ab_user）** | 1-5人 | 10-50人 |
| **ロール・権限** | 5-10個 | 50-100個 |
| **データセット（tables）** | 5-10個 | 50-100個 |
| **データベース接続（dbs）** | 1-2個 | 10-20個 |

### 10-3. データ量の推定計算

**重要**: 実際のデータはBigQueryにあるため、SupersetのPostgreSQLに保存されるのはメタデータ（チャート・ダッシュボードの定義）のみです。クライアント数が増えても、データ量の増加は限定的です。

#### 各テーブルのデータサイズ（概算）

1. **slices（チャート）テーブル**
   - 1レコード: 約10-50KB（`params`、`query_context`がJSONで大きい）
   - チャート定義のみ（実際のデータはBigQueryに保存）
   - 50-100個: 約500KB-5MB
   - 500-1,000個: 約5-50MB

2. **dashboards（ダッシュボード）テーブル**
   - 1レコード: 約5-20KB（`position_json`、`json_metadata`が大きい）
   - ダッシュボード定義のみ（実際のデータはBigQueryに保存）
   - 10-20個: 約50KB-400KB
   - 100-200個: 約500KB-4MB

3. **その他のテーブル**
   - ユーザー、ロール、権限: 約1-2MB（クライアント数に比例して増加）
   - データセット定義（`tables`）: 約500KB-1MB（テーブル名、カラム情報のみ）
   - データベース接続（`dbs`）: 約100KB（接続文字列のみ）
   - システムテーブル、インデックス: 約2-5MB

#### 10クライアント時の総データ量

**最小ケース（小規模運用、チャート数少なめ）:**
- チャート: 500個 × 10KB = 5MB
- ダッシュボード: 100個 × 5KB = 500KB
- ユーザー・権限: 約2MB
- その他: 約1MB
- **合計: 約8.5MB**

**標準ケース（中規模運用、チャート数標準）:**
- チャート: 750個 × 30KB = 22.5MB
- ダッシュボード: 150個 × 10KB = 1.5MB
- ユーザー・権限: 約3MB
- その他: 約2MB
- **合計: 約29MB**

**最大ケース（大規模運用、チャート数多め）:**
- チャート: 1,000個 × 50KB = 50MB
- ダッシュボード: 200個 × 20KB = 4MB
- ユーザー・権限: 約5MB
- その他: 約5MB
- **合計: 約64MB**

**注意**: 実際のビジネスデータ（GA4データ、広告データなど）はBigQueryに保存されているため、SupersetのPostgreSQLのサイズには影響しません。

### 10-4. Supabase無料枠との比較

**Supabase無料枠:**
- ストレージ: **500MB**
- バックアップ: 2時間ごと（7日間保持）

**10クライアント時のデータ量:**
- 最小ケース: 8.5MB ✅ **無料枠内**
- 標準ケース: 29MB ✅ **無料枠内**
- 最大ケース: 64MB ✅ **無料枠内**

**結論: 10クライアント程度であれば、Supabase無料枠（500MB）で十分です。**

**さらに重要なポイント:**
- 実際のデータ（GA4データ、広告データなど）はBigQueryに保存されているため、クライアント数が増えてもSupersetのPostgreSQLのサイズはほとんど増えません
- 増えるのはメタデータ（チャート・ダッシュボードの定義）のみ
- したがって、**50-100クライアントでもSupabase無料枠で十分な可能性が高い**です

### 10-5. 無料枠を超える目安

**Supabase無料枠（500MB）を超える可能性があるケース:**

1. **20クライアント以上**
   - 推定データ量: 約60-130MB（標準ケース）
   - まだ無料枠内ですが、余裕が減る

2. **50クライアント以上**
   - 推定データ量: 約150-320MB（標準ケース）
   - 無料枠内ですが、バックアップ容量も考慮が必要

3. **100クライアント以上**
   - 推定データ量: 約300-640MB（標準ケース）
   - 無料枠ギリギリ、または超過の可能性

4. **チャート数が異常に多い場合**
   - 1クライアントあたり200個以上のチャート
   - 複雑なクエリ（`query_context`が大きい）

### 10-6. 推奨戦略（データ量ベース）

**重要**: 実際のデータはBigQueryにあるため、SupersetのPostgreSQLのサイズはクライアント数に比例して大きく増加しません。

| クライアント数 | 推定データ量 | 推奨サービス | 理由 |
|--------------|------------|------------|------|
| **1-10社** | 8-64MB | **Supabase無料枠** | 無料枠内、コスト0 |
| **10-50社** | 64-150MB | **Supabase無料枠** | まだ無料枠内、監視必要 |
| **50-100社** | 150-300MB | **Supabase無料枠** または **Supabase有料** | 無料枠内の可能性が高い |
| **100社以上** | 300MB以上 | **Supabase有料** または **Cloud SQL最小** | 無料枠超過の可能性、移行検討 |
| **200社以上** | 500MB以上 | **Cloud SQL標準** | スケーラビリティ、パフォーマンス、セキュリティ |

**注意**: データ量よりも、**パフォーマンス**や**セキュリティ要件**で選択を判断することを推奨します。

### 10-7. データ量の監視方法

```sql
-- データベース全体のサイズ
SELECT pg_size_pretty(pg_database_size('superset')) as database_size;

-- テーブルごとのサイズ
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- チャート数・ダッシュボード数
SELECT COUNT(*) as chart_count FROM slices;
SELECT COUNT(*) as dashboard_count FROM dashboards;
```

### 10-8. データ量削減のヒント

1. **不要なチャート・ダッシュボードの削除**
   - 使用されていないチャートを定期的に削除

2. **`query_context`の最適化**
   - 複雑なクエリを簡素化
   - 不要なメタデータを削除

3. **バックアップの最適化**
   - 古いバックアップを削除
   - バックアップ保持期間を調整

4. **データベースのバキューム**
   ```sql
  VACUUM ANALYZE;
  ```

---

## 8. トラブルシューティング

### チャートが表示されない
1. **データベース接続確認**
   ```bash
   docker compose exec db psql -U superset -d superset -c \
     "SELECT id, slice_name FROM slices WHERE id = 258;"
   ```
2. **チャートが存在するか確認**
   - Superset UIで `Charts` → 検索
   - APIで `GET /api/v1/chart/258` を実行

### ダッシュボードが空になる
1. **関連チャートの確認**
   ```bash
   docker compose exec db psql -U superset -d superset -c \
     "SELECT slice_id FROM dashboard_slices WHERE dashboard_id = 19;"
   ```
2. **チャートが削除されていないか確認**
   - `dashboard_slices` にレコードがあっても、`slices` テーブルから削除されている可能性

### データベース接続エラー
1. **コンテナの状態確認**
   ```bash
   docker compose ps db
   ```
2. **ログ確認**
   ```bash
   docker compose logs db
   ```

---

## まとめ

### 共通事項
- **保存場所**: PostgreSQLデータベース（`slices`、`dashboards`、`dashboard_slices`テーブル）
- **主要テーブル**: `slices`（チャート）、`dashboards`（ダッシュボード）、`dashboard_slices`（関連）
- **データ構造**: 環境が変わっても同じテーブル構造・同じデータ形式

### Docker Compose環境
- **データベース**: Dockerコンテナ内のPostgreSQL
- **保存場所**: Docker Volume `superset_db_home`
- **バックアップ**: `pg_dump` または Superset Export API
- **重要**: ボリュームを削除すると全て失われる

### Cloud Run環境
- **データベース**: **Cloud SQL for PostgreSQL**（外部サービス）
- **保存場所**: Cloud SQLインスタンス内
- **バックアップ**: Cloud SQL自動バックアップ + GCSへの定期エクスポート
- **重要**: Cloud Runはステートレスなため、データベースは必ず外部サービスとして管理
- **メリット**: 自動バックアップ、ポイントインタイムリカバリ、高可用性

### 移行時の注意
- Docker Compose → Cloud Run: データベースダンプをCloud SQLにインポート
- Cloud Run → Docker Compose: Cloud SQLからダンプを取得してローカルDBに復元
- **データ構造は同じ**ため、ダンプ/復元で簡単に移行可能

