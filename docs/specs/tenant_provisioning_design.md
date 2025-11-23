# テナントプロビジョニング設計（テンプレート展開）

## 概要
新しいアカウント（テナント）を追加する際に、チャート・ダッシュボードのテンプレートをコピーしてすぐに作成できる機能の設計。

**用語**: 「テンプレート展開」「プロビジョニング」「テンプレートコピー」などと呼ばれます。

---

## 1. 実現方法

### 1-1. SupersetのExport/Import APIを使用

Supersetには、ダッシュボード・チャートをJSON/YAML形式でエクスポート/インポートするAPIが用意されています。

- **Export API**: `/api/v1/dashboard/export/`、`/api/v1/chart/export/`
- **Import API**: `/api/v1/dashboard/import/`、`/api/v1/chart/import/`

### 1-2. 処理フロー

```
1. テンプレートの準備（事前に作成）
   ↓
2. テンプレートをJSON/YAML形式でエクスポート
   ↓
3. テナント追加時にテンプレートを読み込み
   ↓
4. テナント固有の情報に置き換え（Dataset ID、Database IDなど）
   ↓
5. Import APIで新しいテナントにインポート
```

---

## 2. テンプレートの準備

### 2-1. テンプレートダッシュボードの作成

1. **マスターテナントでダッシュボードを作成**
   - 例: 「Google Ads Performance Dashboard」
   - チャートを配置
   - 設定を完了

2. **テンプレートとしてエクスポート**
   ```bash
   # Export APIでエクスポート
   curl -X GET \
     -H "Authorization: Bearer $TOKEN" \
     "https://superset.example.com/api/v1/dashboard/export/?q=(ids:!(19))" \
     -o template_dashboard.json
   ```

3. **テンプレートファイルを保存**
   - `templates/dashboards/google_ads_dashboard.json`
   - `templates/dashboards/funnel_analysis_dashboard.json`
   - など

### 2-2. テンプレートの構造

エクスポートされたJSONには以下が含まれます：

```json
{
  "dashboard_title": "Google Ads Performance Dashboard",
  "position": {
    // チャートの配置情報
  },
  "charts": [
    {
      "slice_name": "Total Cost",
      "viz_type": "big_number_total",
      "datasource_id": 27,
      "datasource_type": "table",
      "params": {
        // チャート設定
      }
    }
  ],
  "datasets": [
    {
      "table_name": "v_ga_ads_performance",
      "database_id": 2
    }
  ]
}
```

---

## 3. テナント追加時の処理

### 3-1. プロビジョニングスクリプト

```python
import json
import requests
from typing import Dict, List

class TenantProvisioner:
    def __init__(self, superset_url: str, admin_token: str):
        self.superset_url = superset_url
        self.admin_token = admin_token
        self.headers = {
            "Authorization": f"Bearer {admin_token}",
            "Content-Type": "application/json"
        }
    
    def provision_tenant(
        self,
        tenant_id: str,
        tenant_name: str,
        bigquery_project: str,
        bigquery_dataset: str
    ) -> Dict:
        """
        テナントをプロビジョニング
        
        Args:
            tenant_id: テナントID
            tenant_name: テナント名
            bigquery_project: BigQueryプロジェクトID
            bigquery_dataset: BigQueryデータセット名
        """
        # 1. Database接続を作成
        database_id = self.create_database(
            tenant_id=tenant_id,
            bigquery_project=bigquery_project,
            bigquery_dataset=bigquery_dataset
        )
        
        # 2. Dataset（テーブル）を作成
        dataset_ids = self.create_datasets(
            tenant_id=tenant_id,
            database_id=database_id,
            bigquery_dataset=bigquery_dataset
        )
        
        # 3. ロールを作成
        role_id = self.create_roles(tenant_id=tenant_id)
        
        # 4. ユーザーを作成
        user_id = self.create_user(
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            role_id=role_id
        )
        
        # 5. テンプレートからダッシュボードを作成
        dashboard_ids = self.create_dashboards_from_templates(
            tenant_id=tenant_id,
            database_id=database_id,
            dataset_ids=dataset_ids,
            user_id=user_id
        )
        
        # 6. ユーザー情報を取得（ログイン情報を含む）
        user_info = self.get_user_info(user_id)
        
        return {
            "tenant_id": tenant_id,
            "database_id": database_id,
            "dataset_ids": dataset_ids,
            "role_id": role_id,
            "user_id": user_id,
            "dashboard_ids": dashboard_ids,
            "user_info": user_info  # ログインID・パスワードを含む
        }
    
    def get_user_info(self, user_id: int) -> Dict:
        """ユーザー情報を取得（ログイン情報を含む）"""
        response = requests.get(
            f"{self.superset_url}/api/v1/security/users/{user_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["result"]
    
    def create_database(
        self,
        tenant_id: str,
        bigquery_project: str,
        bigquery_dataset: str
    ) -> int:
        """BigQuery Database接続を作成"""
        payload = {
            "database_name": f"{tenant_id}_bigquery",
            "sqlalchemy_uri": f"bigquery://{bigquery_project}/{bigquery_dataset}",
            "extra": json.dumps({
                "credentials_info": {
                    "project_id": bigquery_project
                }
            })
        }
        
        response = requests.post(
            f"{self.superset_url}/api/v1/database/",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()["result"]["id"]
    
    def create_datasets(
        self,
        tenant_id: str,
        database_id: int,
        bigquery_dataset: str
    ) -> Dict[str, int]:
        """Dataset（テーブル）を作成"""
        datasets = {
            "v_ga_ads_performance": f"{bigquery_dataset}.v_ga_ads_performance",
            "v_ga_sessions": f"{bigquery_dataset}.v_ga_sessions",
            "v_ga_content_performance": f"{bigquery_dataset}.v_ga_content_performance"
        }
        
        dataset_ids = {}
        for table_name, full_table_name in datasets.items():
            payload = {
                "database_id": database_id,
                "table_name": table_name,
                "schema": bigquery_dataset,
                "sql": f"SELECT * FROM `{full_table_name}`"
            }
            
            response = requests.post(
                f"{self.superset_url}/api/v1/dataset/",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            dataset_ids[table_name] = response.json()["result"]["id"]
        
        return dataset_ids
    
    def create_roles(self, tenant_id: str) -> int:
        """テナント用ロールを作成"""
        # テナント管理者ロール
        admin_role_payload = {
            "name": f"{tenant_id}_admin",
            "permissions": [
                # Database/Datasetへのアクセス権限
                {"permission_name": "database_access", "resource_name": f"{tenant_id}_bigquery"},
                {"permission_name": "dataset_access", "resource_name": f"{tenant_id}_v_ga_ads_performance"},
                {"permission_name": "dataset_access", "resource_name": f"{tenant_id}_v_ga_sessions"},
                # ダッシュボード・チャートの作成・編集権限
                {"permission_name": "can_write", "resource_name": "Dashboard"},
                {"permission_name": "can_write", "resource_name": "Chart"},
                # SQL Labの使用権限
                {"permission_name": "can_sql_json", "resource_name": f"{tenant_id}_bigquery"},
            ]
        }
        
        response = requests.post(
            f"{self.superset_url}/api/v1/security/roles/",
            headers=self.headers,
            json=admin_role_payload
        )
        response.raise_for_status()
        return response.json()["result"]["id"]
    
    def create_user(
        self,
        tenant_id: str,
        tenant_name: str,
        role_id: int,
        username: str = None,
        password: str = None,
        email: str = None
    ) -> Dict[str, any]:
        """
        テナント管理者ユーザーを作成
        
        Args:
            tenant_id: テナントID
            tenant_name: テナント名
            role_id: ロールID
            username: ログインID（指定がない場合は自動生成）
            password: パスワード（指定がない場合は自動生成）
            email: メールアドレス（指定がない場合は自動生成）
        
        Returns:
            {"user_id": int, "username": str, "password": str, "email": str}
        """
        # デフォルト値の設定
        if username is None:
            username = f"{tenant_id}_admin"
        if password is None:
            import secrets
            password = secrets.token_urlsafe(16)  # ランダムパスワード生成
        if email is None:
            email = f"{tenant_id}@example.com"
        
        payload = {
            "username": username,
            "email": email,
            "first_name": tenant_name,
            "last_name": "Admin",
            "active": True,
            "roles": [role_id],
            "password": password  # 初回パスワード
        }
        
        response = requests.post(
            f"{self.superset_url}/api/v1/security/users/",
            headers=self.headers,
            json=payload
        )
        response.raise_for_status()
        user_id = response.json()["result"]["id"]
        
        return {
            "user_id": user_id,
            "username": username,
            "password": password,  # 初回ログイン用パスワード（安全に保管・通知）
            "email": email
        }
    
    def create_dashboards_from_templates(
        self,
        tenant_id: str,
        database_id: int,
        dataset_ids: Dict[str, int],
        user_id: int
    ) -> List[int]:
        """テンプレートからダッシュボードを作成"""
        template_files = [
            "templates/dashboards/google_ads_dashboard.json",
            "templates/dashboards/funnel_analysis_dashboard.json",
            "templates/dashboards/device_analysis_dashboard.json"
        ]
        
        dashboard_ids = []
        for template_file in template_files:
            # テンプレートを読み込み
            with open(template_file, "r") as f:
                template = json.load(f)
            
            # テナント固有の情報に置き換え
            modified_template = self.replace_template_ids(
                template=template,
                database_id=database_id,
                dataset_ids=dataset_ids,
                tenant_id=tenant_id
            )
            
            # Import APIでインポート
            dashboard_id = self.import_dashboard(
                dashboard_data=modified_template,
                user_id=user_id
            )
            dashboard_ids.append(dashboard_id)
        
        return dashboard_ids
    
    def replace_template_ids(
        self,
        template: Dict,
        database_id: int,
        dataset_ids: Dict[str, int],
        tenant_id: str
    ) -> Dict:
        """テンプレート内のIDをテナント固有のIDに置き換え"""
        # ダッシュボードタイトルにテナント名を追加
        if "dashboard_title" in template:
            template["dashboard_title"] = f"{template['dashboard_title']} - {tenant_id}"
        
        # チャート内のDataset IDを置き換え
        if "charts" in template:
            for chart in template["charts"]:
                # datasource_idを新しいDataset IDに置き換え
                if "datasource_id" in chart:
                    old_datasource_id = chart["datasource_id"]
                    # テーブル名から新しいDataset IDを取得
                    table_name = self.get_table_name_from_datasource_id(old_datasource_id)
                    if table_name in dataset_ids:
                        chart["datasource_id"] = dataset_ids[table_name]
                
                # params内のDataset参照も置き換え
                if "params" in chart:
                    params = json.loads(chart["params"]) if isinstance(chart["params"], str) else chart["params"]
                    # 必要に応じてparams内の参照も置き換え
                    chart["params"] = json.dumps(params)
        
        # Dataset定義を置き換え
        if "datasets" in template:
            for dataset in template["datasets"]:
                if "database_id" in dataset:
                    dataset["database_id"] = database_id
                if "table_name" in dataset:
                    # 新しいDataset IDを設定
                    if dataset["table_name"] in dataset_ids:
                        dataset["id"] = dataset_ids[dataset["table_name"]]
        
        return template
    
    def get_table_name_from_datasource_id(self, datasource_id: int) -> str:
        """Datasource IDからテーブル名を取得"""
        response = requests.get(
            f"{self.superset_url}/api/v1/dataset/{datasource_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()["result"]["table_name"]
    
    def import_dashboard(
        self,
        dashboard_data: Dict,
        user_id: int
    ) -> int:
        """ダッシュボードをインポート"""
        # JSONをZIP形式に変換（SupersetのImport APIはZIP形式を要求）
        import zipfile
        import io
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # ダッシュボードYAMLを作成
            import yaml
            dashboard_yaml = yaml.dump(dashboard_data, default_flow_style=False)
            zip_file.writestr("dashboards/dashboard.yaml", dashboard_yaml)
            
            # チャートYAMLも追加
            if "charts" in dashboard_data:
                for chart in dashboard_data["charts"]:
                    chart_yaml = yaml.dump(chart, default_flow_style=False)
                    zip_file.writestr(f"charts/{chart['slice_name']}.yaml", chart_yaml)
        
        zip_buffer.seek(0)
        
        # Import APIでインポート
        files = {"formData": ("dashboard.zip", zip_buffer, "application/zip")}
        response = requests.post(
            f"{self.superset_url}/api/v1/dashboard/import/",
            headers={"Authorization": f"Bearer {self.admin_token}"},
            files=files
        )
        response.raise_for_status()
        
        # インポートされたダッシュボードIDを取得
        # （Import APIのレスポンスから取得、または再取得）
        return self.get_dashboard_id_by_title(dashboard_data["dashboard_title"])
    
    def get_dashboard_id_by_title(self, title: str) -> int:
        """タイトルからダッシュボードIDを取得"""
        response = requests.get(
            f"{self.superset_url}/api/v1/dashboard/?q=(filters:!((col:dashboard_title,opr:eq,value:{title})))",
            headers=self.headers
        )
        response.raise_for_status()
        results = response.json()["result"]
        if results:
            return results[0]["id"]
        raise ValueError(f"Dashboard not found: {title}")
```

---

## 4. ユーザー管理・認証

### 4-1. ログインID・パスワードの管理

**各テナント（お客さん）ごとに異なるログインID・パスワードを管理します。**

#### ユーザーアカウントの作成

```python
# テナント追加時にユーザーを作成
user_info = provisioner.create_user(
    tenant_id="customer_a",
    tenant_name="Customer A",
    role_id=role_id,
    username="customer_a_admin",  # ログインID
    password="SecurePassword123!",  # パスワード
    email="admin@customer-a.com"
)

# 返り値
# {
#     "user_id": 123,
#     "username": "customer_a_admin",
#     "password": "SecurePassword123!",
#     "email": "admin@customer-a.com"
# }
```

#### ログイン情報の管理

**重要**: パスワードは安全に保管・通知する必要があります。

```python
class TenantUserManager:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def store_tenant_credentials(
        self,
        tenant_id: str,
        username: str,
        password: str,
        email: str
    ):
        """テナントの認証情報を安全に保存"""
        # パスワードはハッシュ化して保存（Supersetが管理）
        # ここではメタデータのみ保存
        query = """
        INSERT INTO tenants (tenant_id, username, email, created_at)
        VALUES (%s, %s, %s, NOW())
        """
        self.db.execute(query, (tenant_id, username, email))
    
    def get_tenant_credentials(self, tenant_id: str) -> Dict:
        """テナントの認証情報を取得"""
        query = """
        SELECT tenant_id, username, email
        FROM tenants
        WHERE tenant_id = %s
        """
        result = self.db.fetch_one(query, (tenant_id,))
        return result
```

### 4-2. ログインの流れ

```
1. お客さんがSupersetにアクセス
   ↓
2. ログイン画面でログインID・パスワードを入力
   ↓
3. Supersetが認証（Superset内蔵Auth DB）
   ↓
4. ログイン成功 → テナント用ロールが適用される
   ↓
5. 自分のテナントのデータのみにアクセス可能
```

### 4-3. データ分離の仕組み

#### ロールベースアクセス制御（RBAC）

```python
# テナントごとに異なるロールを作成
roles = {
    "customer_a_admin": {
        "permissions": [
            "database_access:customer_a_bigquery",
            "dataset_access:customer_a_v_ga_ads_performance",
            "can_write:Dashboard",
            "can_write:Chart"
        ]
    },
    "customer_b_admin": {
        "permissions": [
            "database_access:customer_b_bigquery",
            "dataset_access:customer_b_v_ga_ads_performance",
            "can_write:Dashboard",
            "can_write:Chart"
        ]
    }
}
```

#### データアクセスの制限

- **Database接続**: テナントごとに異なるBigQuery接続
- **Dataset**: テナントごとに異なるDataset ID
- **ダッシュボード**: テナントごとに異なるダッシュボードID
- **ロール**: テナントごとに異なるロール（アクセス権限を分離）

### 4-4. 複数ユーザーの管理

1テナントに複数のユーザーを追加することも可能です。

```python
# テナントに追加のユーザーを作成
def add_user_to_tenant(
    tenant_id: str,
    username: str,
    password: str,
    email: str,
    role_type: str = "viewer"  # "admin" or "viewer"
):
    """テナントにユーザーを追加"""
    # テナントのロールを取得
    role_id = get_tenant_role_id(tenant_id, role_type)
    
    # ユーザーを作成
    user_info = provisioner.create_user(
        tenant_id=tenant_id,
        tenant_name=tenant_id,
        role_id=role_id,
        username=username,
        password=password,
        email=email
    )
    
    return user_info
```

### 4-5. パスワードリセット

```python
def reset_tenant_password(
    tenant_id: str,
    username: str,
    new_password: str
):
    """テナントユーザーのパスワードをリセット"""
    # ユーザーIDを取得
    user_id = get_user_id_by_username(username)
    
    # パスワードを更新
    payload = {
        "password": new_password
    }
    
    response = requests.put(
        f"{SUPERSET_URL}/api/v1/security/users/{user_id}",
        headers=headers,
        json=payload
    )
    response.raise_for_status()
```

### 4-6. テナント情報の管理テーブル

```sql
-- テナント情報を管理するテーブル
CREATE TABLE tenants (
    tenant_id VARCHAR(255) PRIMARY KEY,
    tenant_name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    database_id INTEGER,
    role_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- テナントの認証情報（メタデータのみ、パスワードはSupersetが管理）
CREATE TABLE tenant_credentials (
    tenant_id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires_at TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
);
```

---

## 5. 使用例

### 4-1. CLIコマンド

```bash
# テナントをプロビジョニング
python scripts/provision_tenant.py \
  --tenant-id customer_a \
  --tenant-name "Customer A" \
  --bigquery-project analytics_456071139 \
  --bigquery-dataset customer_a_ga4
```

### 5-2. Pythonスクリプト

```python
from scripts.provision_tenant import TenantProvisioner

provisioner = TenantProvisioner(
    superset_url="https://superset.example.com",
    admin_token="your_admin_token"
)

# テナントをプロビジョニング（ユーザー作成含む）
result = provisioner.provision_tenant(
    tenant_id="customer_a",
    tenant_name="Customer A",
    bigquery_project="analytics_456071139",
    bigquery_dataset="customer_a_ga4"
)

print(f"Tenant provisioned: {result}")
print(f"Login ID: {result['user_info']['username']}")
print(f"Password: {result['user_info']['password']}")  # 初回ログイン用
print(f"Email: {result['user_info']['email']}")

# お客さんにログイン情報を通知
send_welcome_email(
    email=result['user_info']['email'],
    username=result['user_info']['username'],
    password=result['user_info']['password'],
    login_url="https://superset.example.com/login"
)
```

### 5-3. 完全なプロビジョニング例

```python
# 1. テナントをプロビジョニング
result = provisioner.provision_tenant(
    tenant_id="customer_a",
    tenant_name="Customer A",
    bigquery_project="analytics_456071139",
    bigquery_dataset="customer_a_ga4"
)

# 2. ログイン情報を取得
login_info = {
    "username": result['user_info']['username'],  # "customer_a_admin"
    "password": result['user_info']['password'],  # 初回ログイン用パスワード
    "email": result['user_info']['email']
}

# 3. お客さんに通知
print(f"""
テナント作成が完了しました。

【ログイン情報】
ログインURL: https://superset.example.com/login
ログインID: {login_info['username']}
パスワード: {login_info['password']}

【注意事項】
- 初回ログイン時にパスワードの変更を推奨します
- このパスワードは安全に保管してください
""")

# 4. メールで通知（オプション）
send_welcome_email(
    to=login_info['email'],
    subject="Supersetアカウント作成完了",
    body=f"""
    Customer A様
    
    Supersetアカウントが作成されました。
    
    ログインURL: https://superset.example.com/login
    ログインID: {login_info['username']}
    パスワード: {login_info['password']}
    
    初回ログイン時にパスワードの変更をお願いします。
    """
)
```

---

## 5. テンプレートの管理

### 5-1. テンプレートファイルの構造

```
templates/
├── dashboards/
│   ├── google_ads_dashboard.json
│   ├── funnel_analysis_dashboard.json
│   ├── device_analysis_dashboard.json
│   └── ...
├── charts/
│   ├── chart_templates.json
│   └── ...
└── datasets/
    └── dataset_definitions.json
```

### 5-2. テンプレートのバージョン管理

- Gitでテンプレートを管理
- バージョンタグを付与
- テンプレート更新時は新しいバージョンを作成

### 5-3. テンプレートの更新

```python
def update_template(
    template_name: str,
    dashboard_id: int
):
    """既存のダッシュボードからテンプレートを更新"""
    # Export APIでエクスポート
    response = requests.get(
        f"{SUPERSET_URL}/api/v1/dashboard/export/?q=(ids:!({dashboard_id}))",
        headers=headers
    )
    
    # テンプレートファイルに保存
    with open(f"templates/dashboards/{template_name}.json", "w") as f:
        json.dump(response.json(), f, indent=2)
```

---

## 6. 注意事項

### 6-1. IDの置き換え

- **Database ID**: テナントごとに異なる
- **Dataset ID**: テナントごとに異なる
- **Chart ID**: 新規作成されるため置き換え不要
- **Dashboard ID**: 新規作成されるため置き換え不要

### 6-2. 権限の設定

- テナント用ロールに適切な権限を付与
- Database/Datasetへのアクセス権限を設定
- ダッシュボードへのアクセス権限を設定

### 6-3. エラーハンドリング

- テンプレートファイルの存在確認
- Import APIのエラーハンドリング
- ロールバック処理（失敗時のクリーンアップ）

---

## 7. 管理者（Admin）のアクセス権限

### 7-1. Adminユーザーの権限

**重要**: SupersetのAdminロールは、**全てのテナントのデータにアクセス可能**です。

#### Adminロールの特徴

- ✅ **全リソースへのアクセス**: 全てのDatabase、Dataset、Dashboard、Chartにアクセス可能
- ✅ **全ユーザーの管理**: ユーザー作成・削除・権限変更が可能
- ✅ **全ロールの管理**: ロール作成・削除・権限変更が可能
- ✅ **全テナントのデータ閲覧**: お客さんのデータも閲覧可能

#### コードでの確認

```python
# Supersetのセキュリティマネージャー
def is_admin(self) -> bool:
    """Adminユーザーかどうかをチェック"""
    return get_conf()["AUTH_ROLE_ADMIN"] in [
        role.name for role in self.get_user_roles()
    ]

def raise_for_ownership(self, resource: Model) -> None:
    """リソースの所有権をチェック（Adminは全リソースのオーナーとみなされる）"""
    if self.is_admin():
        return  # Adminは常にアクセス可能
    # ... 通常の所有権チェック
```

### 7-2. セキュリティ・プライバシーの考慮事項

#### 必要な対策

1. **監査ログ**
   - Adminユーザーのアクセスを全て記録
   - どのテナントのデータにアクセスしたかを記録
   - アクセス理由を記録

2. **アクセス制限**
   - Adminユーザーを最小限に（必要最小限の人数のみ）
   - 2要素認証（2FA）を必須化
   - 定期的なパスワード変更

3. **プライバシーポリシー**
   - お客さんにAdminアクセスの可能性を明示
   - サポート・トラブルシューティング目的でのみアクセス
   - データの機密性を保証

### 7-3. 監査ログの実装

```python
import logging
from datetime import datetime

class AdminAccessLogger:
    def __init__(self):
        self.logger = logging.getLogger("admin_access")
        self.logger.setLevel(logging.INFO)
        
        # ファイルハンドラーを追加
        handler = logging.FileHandler("logs/admin_access.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def log_admin_access(
        self,
        admin_username: str,
        tenant_id: str,
        resource_type: str,
        resource_id: int,
        action: str,
        reason: str = None
    ):
        """Adminユーザーのアクセスを記録"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "admin_username": admin_username,
            "tenant_id": tenant_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "reason": reason
        }
        
        self.logger.info(json.dumps(log_entry))
        
        # BigQuery Audit Logにも記録（オプション）
        self.log_to_bigquery(log_entry)
    
    def log_to_bigquery(self, log_entry: dict):
        """BigQuery Audit Logに記録"""
        # BigQueryに監査ログを保存
        pass
```

### 7-4. Adminアクセスの制御（オプション）

#### カスタムセキュリティマネージャー

必要に応じて、Adminのアクセスを制限することも可能です（ただし、通常は推奨されません）。

```python
from superset.security.manager import SupersetSecurityManager

class CustomSecurityManager(SupersetSecurityManager):
    def can_access_database(self, database, raise_error=True):
        """Databaseへのアクセス権限をチェック"""
        # Adminは全Databaseにアクセス可能
        if self.is_admin():
            # 監査ログを記録
            self.log_admin_access(
                admin_username=g.user.username,
                tenant_id=self.get_tenant_id_from_database(database),
                resource_type="database",
                resource_id=database.id,
                action="access"
            )
            return True
        
        # 通常の権限チェック
        return super().can_access_database(database, raise_error)
    
    def get_tenant_id_from_database(self, database):
        """DatabaseからテナントIDを取得"""
        # Database名からテナントIDを抽出
        # 例: "customer_a_bigquery" → "customer_a"
        return database.database_name.split("_")[0]
```

### 7-5. 実装例：Adminアクセスの記録

```python
# SupersetのAPIエンドポイントで監査ログを記録
from flask import g
from superset import security_manager

@expose("/api/v1/dashboard/<pk>", methods=("GET",))
@protect()
def get_dashboard(self, pk: int):
    """ダッシュボードを取得（Adminアクセスを記録）"""
    dashboard = self.datamodel.get(pk)
    
    # Adminユーザーの場合、監査ログを記録
    if security_manager.is_admin():
        tenant_id = get_tenant_id_from_dashboard(dashboard)
        admin_logger.log_admin_access(
            admin_username=g.user.username,
            tenant_id=tenant_id,
            resource_type="dashboard",
            resource_id=dashboard.id,
            action="view",
            reason="Support/Troubleshooting"
        )
    
    return self.response(200, result=dashboard)
```

### 7-6. お客さんへの通知

#### プライバシーポリシー

お客さんに以下の点を明示：

```
【データアクセスについて】

当社の管理者（Admin）ユーザーは、以下の目的でのみ
お客様のデータにアクセスする可能性があります：

1. サポート・トラブルシューティング
2. システムメンテナンス
3. セキュリティ監査

全てのアクセスは監査ログに記録され、適切に管理されます。
お客様のデータの機密性は厳重に保護されます。
```

### 7-7. まとめ

#### Adminユーザーのアクセス権限

- ✅ **全テナントのデータにアクセス可能**
- ✅ サポート・トラブルシューティングに必要
- ⚠️ **適切な管理が必要**（監査ログ、アクセス制限、プライバシーポリシー）

#### 推奨事項

1. **監査ログ**: Adminの全アクセスを記録
2. **アクセス制限**: Adminユーザーを最小限に
3. **セキュリティ**: 2FA、定期的なパスワード変更
4. **プライバシー**: お客さんに明示・同意を得る

---

## 8. まとめ

### 実現可能なこと
- ✅ テンプレートからダッシュボード・チャートを自動生成
- ✅ テナント追加時に一括でプロビジョニング
- ✅ IDの自動置き換え（Database ID、Dataset IDなど）
- ✅ **お客さんごとに異なるログインID・パスワードを管理**
- ✅ **ロールベースアクセス制御でデータ分離**

### 重要なポイント

#### 1. ログインID・パスワードの管理
- **各テナント（お客さん）ごとに異なるログインID・パスワード**
- テナント追加時に自動生成、または指定可能
- 初回ログイン用パスワードを安全に通知

#### 2. データ分離
- **ロールベースアクセス制御（RBAC）**でデータを分離
- テナントごとに異なるDatabase接続、Dataset、ダッシュボード
- お客さんは自分のテナントのデータのみにアクセス可能

#### 3. テンプレート展開
- テンプレートからダッシュボード・チャートを自動生成
- IDの自動置き換え（Database ID、Dataset IDなど）

### 実装のポイント
1. **Export/Import API**を使用
2. **テンプレートファイル**を事前に準備
3. **IDの置き換え**を適切に実装
4. **権限設定**を忘れずに
5. **ログイン情報の安全な管理・通知**

### 推奨実装順序
1. **フェーズ1**: テンプレートのエクスポート・保存
2. **フェーズ2**: 基本的なプロビジョニングスクリプト
3. **フェーズ3**: ユーザー作成・ログイン情報管理
4. **フェーズ4**: ID置き換えの実装
5. **フェーズ5**: エラーハンドリング・ロールバック

### お客さんごとの管理フロー

```
1. テナント追加
   ↓
2. ログインID・パスワードを生成（または指定）
   ↓
3. Database/Dataset/ロール/ユーザーを作成
   ↓
4. テンプレートからダッシュボード・チャートを作成
   ↓
5. ログイン情報をお客さんに通知
   ↓
6. お客さんがログイン → 自分のテナントのデータのみにアクセス可能
```

