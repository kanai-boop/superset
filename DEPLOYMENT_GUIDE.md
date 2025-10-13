# Superset ローカル環境構築ガイド

## 概要
Apache Supersetをローカル環境（Docker）で起動する手順をまとめたドキュメントです。

## 前提条件
- Docker Desktop がインストールされていること
- WSL2（Windows）またはLinux/Mac環境
- Git がインストールされていること
- 最低8GB以上のメモリ

## 手順

### 1. リポジトリのクローン

```bash
git clone https://github.com/kanai-boop/superset.git
cd superset
```

### 2. ブランチの作成（任意）

```bash
git checkout -b dev-yourname
```

### 3. Docker起動（推奨: ビルド済みイメージ使用）

**⚠️ 重要**: `docker-compose.yml`を使うとフロントエンドのビルドに30分以上かかります。
ビルド済みイメージを使用することを推奨します。

```bash
# ビルド済みイメージで起動（推奨）
docker compose -f docker-compose-image-tag.yml up -d
```

起動完了まで5-10分程度かかります。

### 4. 起動確認

```bash
docker compose -f docker-compose-image-tag.yml ps
```

以下のコンテナが`Up`かつ`healthy`になっていればOK:
- superset_app
- superset_cache
- superset_db
- superset_worker
- superset_worker_beat

### 5. アクセス

ブラウザで以下にアクセス:
- **URL**: http://localhost:8088
- **ユーザー名**: `admin`
- **パスワード**: `admin`

## BigQuery接続（オプション）

### BigQueryドライバーのインストール

```bash
# コンテナにBigQueryドライバーをインストール
docker compose -f docker-compose-image-tag.yml exec superset pip install pybigquery

# Supersetを再起動
docker compose -f docker-compose-image-tag.yml restart superset
```

### BigQuery接続設定

1. Superset UIにログイン
2. `Settings` → `Database Connections` → `+ Database`
3. `Google BigQuery`を選択
4. 以下を入力:
   - **SQLALCHEMY URI**: `bigquery://your-project-id`
   - **Service Account JSON**: BigQueryのサービスアカウントキーを貼り付け
5. `Test Connection`で接続確認
6. `Connect`をクリック

### BigQueryのデータを使う

**SQL Labでクエリ実行:**
```sql
-- データセット名を必ず指定する
SELECT * FROM `your_dataset_name.your_table_name` LIMIT 10;
```

**データセットとして登録:**
1. `Data` → `Datasets` → `+ Dataset`
2. 入力:
   - **Database**: Google BigQuery
   - **Schema**: データセット名
   - **Table**: テーブル名

## よく使うコマンド

### コンテナの操作

```bash
# 停止
docker compose -f docker-compose-image-tag.yml down

# 起動
docker compose -f docker-compose-image-tag.yml up -d

# ログ確認
docker compose -f docker-compose-image-tag.yml logs -f superset

# 特定のコンテナに入る
docker compose -f docker-compose-image-tag.yml exec superset bash
```

### PostgreSQLの操作

```bash
# テーブル一覧
docker compose -f docker-compose-image-tag.yml exec db psql -U superset -d superset -c "\dt"

# ユーザー一覧
docker compose -f docker-compose-image-tag.yml exec db psql -U superset -d superset -c "SELECT id, username, email FROM ab_user;"

# ダッシュボード一覧
docker compose -f docker-compose-image-tag.yml exec db psql -U superset -d superset -c "SELECT id, dashboard_title, slug, published FROM dashboards ORDER BY id;"

# データベース接続一覧
docker compose -f docker-compose-image-tag.yml exec db psql -U superset -d superset -c "SELECT id, database_name, sqlalchemy_uri FROM dbs;"

# 対話モードで接続
docker compose -f docker-compose-image-tag.yml exec db psql -U superset -d superset
# 終了は \q または Ctrl+D
```

## トラブルシューティング

### ログイン画面から進まない

**症状**: ログイン画面にアクセスできるが、UIが正しく表示されない

**原因**: フロントエンドのビルドが完了していない、または静的ファイルが存在しない

**解決方法**:
1. `docker-compose-image-tag.yml`を使用してビルド済みイメージで起動する
2. コンテナのログを確認: `docker compose -f docker-compose-image-tag.yml logs superset`

### npm installが終わらない

**症状**: ローカルで`npm install`を実行すると10分以上かかる

**原因**: Supersetは大規模プロジェクトで依存関係が多い

**解決方法**:
- フロントエンド開発をしない場合: Docker内のビルド済みイメージを使用（推奨）
- フロントエンド開発をする場合: 気長に待つ（初回15-20分程度）

### BigQueryで "must be qualified with a dataset" エラー

**症状**:
```
Table "your_table" must be qualified with a dataset (e.g. dataset.table)
```

**解決方法**:
テーブル名の前にデータセット名を追加:
```sql
-- ❌ 間違い
SELECT * FROM your_table

-- ✅ 正しい
SELECT * FROM `dataset_name.your_table`
```

### コンテナが起動しない

**確認事項**:
1. Dockerが起動しているか確認
2. ポート8088が他のプロセスに使われていないか確認
   ```bash
   # Windows/WSL
   netstat -ano | findstr :8088

   # Linux/Mac
   lsof -i :8088
   ```
3. メモリが十分か確認（最低8GB推奨）

## ディレクトリ構造

```
superset/
├── docker/                      # Docker関連設定
│   ├── .env                    # 環境変数（デフォルト設定）
│   └── docker-init.sh          # 初期化スクリプト
├── docker-compose.yml           # 開発用（ビルドあり、時間がかかる）
├── docker-compose-image-tag.yml # 本番用イメージ（推奨）
├── superset/                    # Pythonバックエンド
├── superset-frontend/           # Reactフロントエンド
└── DEPLOYMENT_GUIDE.md          # このファイル
```

## 参考リンク

- [Apache Superset 公式ドキュメント](https://superset.apache.org/)
- [Docker Compose での起動方法](https://superset.apache.org/docs/installation/docker-compose)
- [BigQuery接続ガイド](https://superset.apache.org/docs/configuration/databases#google-bigquery)

## 更新履歴

- 2025-10-13: 初版作成
