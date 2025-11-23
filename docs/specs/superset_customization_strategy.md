# Supersetカスタマイズ戦略

## 概要
Supersetの標準機能では実現できないユーザー体験要件を、どのように実装するかの戦略。

---

## 1. 現状の課題

### 1-1. Superset標準機能の制約

#### 実現できない機能
- ❌ カスタムオンボーディングフロー
- ❌ カスタムエラーメッセージ
- ❌ カスタムヘルプコンテンツ
- ❌ カスタムサポートフォーム
- ❌ ウェルカムダッシュボードの自動表示
- ❌ カスタムUI要素

#### 実現可能な機能（標準機能）
- ✅ ダッシュボード・チャートの作成
- ✅ 基本的な認証・認可
- ✅ データの可視化
- ✅ 基本的なエクスポート機能

---

## 2. カスタマイズ方法の選択肢

### 2-1. アプローチA: プロキシレイヤー（推奨）

#### 概要
Supersetの前段に別のアプリケーション（プロキシ）を配置し、そこでカスタム機能を実装。

#### アーキテクチャ
```
ユーザー
  ↓
プロキシアプリ（FastAPI/Flask）
  ├─ オンボーディングフロー
  ├─ カスタムヘルプ
  ├─ サポートフォーム
  └─ カスタムエラーページ
  ↓
Superset（標準機能のみ使用）
```

#### メリット
- ✅ Supersetのアップグレードに影響されない
- ✅ カスタマイズが容易
- ✅ 段階的に機能を追加できる
- ✅ Supersetの標準機能をそのまま使える

#### デメリット
- ❌ 追加のアプリケーションが必要
- ❌ セッション管理が複雑になる可能性

#### 実装例
```python
# FastAPIプロキシアプリ
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
import httpx

app = FastAPI()

@app.get("/")
async def root(request: Request):
    """ルートパスでオンボーディングチェック"""
    user = get_current_user(request)
    
    # 初回ログインチェック
    if is_first_login(user):
        return RedirectResponse("/onboarding")
    
    # Supersetにプロキシ
    return await proxy_to_superset(request)

@app.get("/onboarding")
async def onboarding(request: Request):
    """オンボーディングページ"""
    return HTMLResponse("""
    <html>
        <head><title>ようこそ</title></head>
        <body>
            <h1>Supersetへようこそ</h1>
            <p>まずはサンプルダッシュボードを見てみましょう</p>
            <a href="/superset/dashboard/welcome">サンプルダッシュボードを見る</a>
        </body>
    </html>
    """)

@app.get("/help")
async def help_page():
    """ヘルプページ"""
    return HTMLResponse("""
    <html>
        <head><title>ヘルプ</title></head>
        <body>
            <h1>使い方ガイド</h1>
            <h2>基本的な使い方</h2>
            <p>...</p>
            <h2>よくある質問</h2>
            <p>...</p>
        </body>
    </html>
    """)

@app.get("/support")
async def support_page():
    """サポートページ"""
    return HTMLResponse("""
    <html>
        <head><title>サポート</title></head>
        <body>
            <h1>お問い合わせ</h1>
            <form action="/support/submit" method="post">
                <textarea name="message" placeholder="お問い合わせ内容"></textarea>
                <button type="submit">送信</button>
            </form>
        </body>
    </html>
    """)

async def proxy_to_superset(request: Request):
    """Supersetにリクエストをプロキシ"""
    async with httpx.AsyncClient() as client:
        # SupersetのURLにリクエストを転送
        response = await client.request(
            method=request.method,
            url=f"http://superset:8088{request.url.path}",
            headers=dict(request.headers),
            params=dict(request.query_params)
        )
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
```

### 2-2. アプローチB: Supersetプラグイン

#### 概要
Supersetのプラグイン機能を使用してカスタム機能を追加。

#### メリット
- ✅ Supersetの標準機能と統合
- ✅ Supersetのアップグレードに追従しやすい

#### デメリット
- ❌ プラグイン開発の知識が必要
- ❌ プラグインAPIの制約がある
- ❌ 実装が複雑

#### 実装例
```python
# Supersetプラグイン
from superset import app
from flask import Blueprint, render_template

custom_bp = Blueprint('custom', __name__)

@custom_bp.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')

app.register_blueprint(custom_bp)
```

### 2-3. アプローチC: Supersetフォーク

#### 概要
Supersetのソースコードをフォークして直接カスタマイズ。

#### メリット
- ✅ 完全なカスタマイズが可能

#### デメリット
- ❌ Supersetのアップグレードが困難
- ❌ メンテナンスコストが高い
- ❌ 推奨されない

---

## 3. MVPでの推奨アプローチ

### 3-1. ハイブリッドアプローチ（推奨）

#### 基本方針
- **プロキシレイヤー**: オンボーディング、ヘルプ、サポート
- **Superset標準機能**: ダッシュボード、チャート、データ可視化
- **最小限のカスタマイズ**: 必要最小限のみ

#### 実装範囲

**プロキシレイヤーで実装**
- ✅ オンボーディングフロー（初回ログイン時のリダイレクト）
- ✅ ヘルプページ（別ページとして実装）
- ✅ サポートフォーム（別ページとして実装）
- ✅ カスタムエラーページ（エラー時のリダイレクト）

**Superset標準機能を使用**
- ✅ ダッシュボード・チャートの作成・表示
- ✅ 認証・認可
- ✅ データの可視化

**最小限のカスタマイズ**
- ⚠️ エラーメッセージのカスタマイズ（可能な範囲で）
- ⚠️ ブランディング（ロゴ、色の変更）

### 3-2. 実装の優先順位

#### フェーズ1: MVP（最小限）
1. **プロキシレイヤーの基本実装**
   - Supersetへのプロキシ
   - 基本的なルーティング

2. **オンボーディング（最小限）**
   - 初回ログイン時のリダイレクト
   - サンプルダッシュボードへのリンク

3. **ヘルプ（最小限）**
   - 基本的な使い方ガイド（別ページ）
   - FAQ（別ページ）

#### フェーズ2: 改善（MVP後）
4. **サポートフォーム**
   - お問い合わせフォーム
   - メール送信機能

5. **エラーハンドリング**
   - カスタムエラーページ
   - エラーメッセージの改善

#### フェーズ3: 本格運用（将来）
6. **高度なカスタマイズ**
   - カスタムUI要素
   - 高度なオンボーディングフロー

---

## 4. 実装例：プロキシレイヤー

### 4-1. 基本的なプロキシアプリ

```python
# app/main.py
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import httpx
import os

app = FastAPI(title="Superset Proxy")

SUPERSET_URL = os.getenv("SUPERSET_URL", "http://superset:8088")

@app.get("/")
async def root(request: Request):
    """ルートパス"""
    # セッション確認
    session = request.cookies.get("session")
    if not session:
        return RedirectResponse("/login")
    
    # 初回ログインチェック（簡易版）
    # 実際にはデータベースでチェック
    if is_first_login(session):
        return RedirectResponse("/onboarding")
    
    # Supersetにプロキシ
    return await proxy_to_superset(request)

@app.get("/onboarding")
async def onboarding():
    """オンボーディングページ"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ようこそ - Superset</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            .button { display: inline-block; padding: 10px 20px; background: #20a7c9; color: white; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>Supersetへようこそ！</h1>
        <p>データ分析を始めましょう。</p>
        <h2>まずはこちらから</h2>
        <ul>
            <li><a href="/superset/dashboard/welcome" class="button">サンプルダッシュボードを見る</a></li>
            <li><a href="/help" class="button">使い方ガイドを見る</a></li>
        </ul>
    </body>
    </html>
    """)

@app.get("/help")
async def help():
    """ヘルプページ"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ヘルプ - Superset</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #333; }
            h2 { color: #666; margin-top: 30px; }
        </style>
    </head>
    <body>
        <h1>使い方ガイド</h1>
        <h2>基本的な使い方</h2>
        <p>ダッシュボードを見るには、左側のメニューから「Dashboards」を選択してください。</p>
        <h2>よくある質問</h2>
        <h3>データが表示されない</h3>
        <p>データの更新に時間がかかることがあります。しばらく待ってから再度お試しください。</p>
        <h3>エラーが発生する</h3>
        <p>問題が続く場合は、<a href="/support">サポート</a>までお問い合わせください。</p>
    </body>
    </html>
    """)

@app.get("/support")
async def support():
    """サポートページ"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>サポート - Superset</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; }
            form { margin-top: 20px; }
            textarea { width: 100%; height: 200px; padding: 10px; }
            button { padding: 10px 20px; background: #20a7c9; color: white; border: none; border-radius: 5px; cursor: pointer; }
        </style>
    </head>
    <body>
        <h1>お問い合わせ</h1>
        <form action="/support/submit" method="post">
            <p>
                <label>お問い合わせ内容</label><br>
                <textarea name="message" required></textarea>
            </p>
            <button type="submit">送信</button>
        </form>
    </body>
    </html>
    """)

@app.post("/support/submit")
async def submit_support(request: Request):
    """サポートリクエストを送信"""
    form = await request.form()
    message = form.get("message")
    
    # メール送信（簡易版）
    # 実際にはメール送信サービスを使用
    send_support_email(message)
    
    return HTMLResponse("""
    <html>
    <body>
        <h1>お問い合わせを受け付けました</h1>
        <p>24時間以内にご返信いたします。</p>
        <a href="/">ダッシュボードに戻る</a>
    </body>
    </html>
    """)

async def proxy_to_superset(request: Request):
    """Supersetにリクエストをプロキシ"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=f"{SUPERSET_URL}{request.url.path}",
                headers={k: v for k, v in request.headers.items() if k.lower() not in ["host", "content-length"]},
                params=dict(request.query_params),
                content=await request.body() if request.method in ["POST", "PUT", "PATCH"] else None,
                timeout=30.0
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers={k: v for k, v in response.headers.items() if k.lower() not in ["content-encoding", "transfer-encoding"]},
                media_type=response.headers.get("content-type")
            )
        except Exception as e:
            return HTMLResponse(f"<h1>エラーが発生しました</h1><p>{str(e)}</p>", status_code=500)

def is_first_login(session: str) -> bool:
    """初回ログインかどうかをチェック（簡易版）"""
    # 実際にはデータベースでチェック
    # ここでは簡易的に実装
    return False

def send_support_email(message: str):
    """サポートメールを送信（簡易版）"""
    # 実際にはメール送信サービスを使用
    print(f"Support request: {message}")
```

### 4-2. Docker Compose設定

```yaml
# docker-compose.yml
version: '3.8'

services:
  proxy:
    build: ./proxy
    ports:
      - "80:8000"
    environment:
      - SUPERSET_URL=http://superset:8088
    depends_on:
      - superset

  superset:
    # 既存のSuperset設定
    ...
```

---

## 5. MVPでの実装方針

### 5-1. 最小限の実装

#### 実装するもの
1. **プロキシレイヤー（最小限）**
   - Supersetへのプロキシ
   - 基本的なルーティング

2. **オンボーディング（最小限）**
   - 初回ログイン時のリダイレクト
   - サンプルダッシュボードへのリンク

3. **ヘルプ（最小限）**
   - 基本的な使い方ガイド（別ページ）
   - FAQ（別ページ）

#### 実装しないもの（後回し）
- ❌ カスタムエラーメッセージ（Superset標準を使用）
- ❌ カスタムUI要素（Superset標準を使用）
- ❌ 高度なオンボーディングフロー（後で追加）

### 5-2. 実装の優先順位

**フェーズ1: MVP（1週間）**
- プロキシレイヤーの基本実装
- オンボーディングページ（最小限）
- ヘルプページ（最小限）

**フェーズ2: 改善（2週間）**
- サポートフォーム
- エラーハンドリングの改善

**フェーズ3: 本格運用（1-3ヶ月）**
- 高度なカスタマイズ
- カスタムUI要素

---

## 6. まとめ

### 推奨アプローチ

**プロキシレイヤー + Superset標準機能**

- ✅ Supersetのアップグレードに影響されない
- ✅ 段階的に機能を追加できる
- ✅ 実装が比較的簡単
- ✅ MVPとして現実的

### MVPでの実装範囲

**最小限の実装**
- プロキシレイヤー（Supersetへのプロキシ）
- オンボーディングページ（最小限）
- ヘルプページ（最小限）

**後回し**
- カスタムエラーメッセージ
- カスタムUI要素
- 高度なオンボーディングフロー

**「まずは動かす。必要になったら追加する。」**

これがMVPの基本方針です。Supersetの標準機能を最大限活用し、必要最小限のカスタマイズのみを行います。

