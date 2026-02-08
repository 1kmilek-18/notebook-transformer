# Stitch MCP サーバー接続手順

[技術評論社の記事](https://gihyo.jp/article/2026/01/google-stitch-mcp)および [Google Stitch](https://stitch.withgoogle.com/) のリモート MCP サーバーを Cursor で使うための手順です。

## 概要

Stitch MCP を使うと、Cursor から以下が可能になります。

- Stitch のデザインからコード（HTML/Tailwind）を取得
- IDE 内でテキストプロンプトから新規画面を生成
- プロジェクト・画面の一覧取得、画像ダウンロード

## 前提

- **Google Cloud のプロジェクト**（Project ID を控えておく）
- **gcloud CLI** のインストール

## 手順 1: gcloud CLI のインストールとログイン

```bash
# 未インストールの場合: https://cloud.google.com/sdk/docs/install を参照

# ユーザー認証
gcloud auth login

# アプリケーションのデフォルト認証（MCP クライアント用）
gcloud auth application-default login
```

## 手順 2: Stitch API の有効化

**このリポジトリでは**、gcloud ログイン済みであれば次のワンライナーで有効化できます。

```bash
./scripts/enable-stitch-api.sh
```

（`GOOGLE_CLOUD_PROJECT` 未設定時は `.cursor/mcp.json` と同じプロジェクト ID を使用します。）

手動で行う場合:

1. [Google Cloud Console](https://console.cloud.google.com/) で対象プロジェクトを選択
2. **API とサービス** → **ライブラリ** で「Stitch API」を検索
3. **Stitch API** (`stitch.googleapis.com`) を有効化

または CLI で:

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable stitch.googleapis.com
# クォータプロジェクトの設定（必要に応じて）
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
```

## 手順 3: Cursor の MCP 設定

### 方法 A: stitch-mcp パッケージ（推奨・stdio）

`stitch-mcp` は Application Default Credentials を使うため、**アクセストークンを手動で取得・更新する必要がありません**。

1. **Cursor** → **Settings** → **MCP** を開く
2. **Add New Server** で以下を追加（または既存の `mcp.json` に追記）:

```json
{
  "mcpServers": {
    "stitch": {
      "command": "npx",
      "args": ["-y", "stitch-mcp"],
      "env": {
        "GOOGLE_CLOUD_PROJECT": "あなたのGoogle CloudのProject ID"
      }
    }
  }
}
```

3. `GOOGLE_CLOUD_PROJECT` を実際の Project ID に置き換える
4. Cursor を再起動するか、MCP サーバーを再接続

### 方法 B: 公式リモート URL（SSE・トークン必要）

公式のリモート MCP は **URL: `https://stitch.googleapis.com/mcp`** で、認証は **HTTP ヘッダーにアクセストークンを付与**する形式です。

- アクセストークンは **約 1 時間で失効**するため、定期的に再取得が必要です。
- トークン取得例:

```bash
# ログイン済みの状態で
gcloud auth print-access-token
```

このトークンを Cursor の MCP 設定でヘッダーとして渡す必要があります。Cursor がリモート MCP のカスタムヘッダーをサポートしている場合、その設定に `Authorization: Bearer <トークン>` を指定してください。サポート状況は [Cursor のドキュメント](https://docs.cursor.com/) で確認してください。

## 利用可能なツール（例）

接続後、Cursor の AI から次のようなツールが利用できます。

| ツール | 説明 |
|--------|------|
| `list_projects` | 所有・共有されているプロジェクト一覧を取得 |
| `list_screens` | 指定プロジェクト内の全画面を取得 |
| `get_project` / `get_screen` | プロジェクト・画面の詳細取得 |
| `generate_screen_from_text` | テキストプロンプトから新規デザインを生成 |
| （その他） | 画面の HTML 取得・画像ダウンロードなど |

## トラブルシューティング

### 「Error - Show Output」と表示される場合

Stitch MCP が起動に失敗しています。**原因の多くは Project ID 未設定**です。

1. **エラー内容の確認**  
   Cursor の MCP 一覧で **「Show Output」** をクリックし、ログを開く。  
   `Project ID not found. Set GOOGLE_CLOUD_PROJECT env var` と出ていれば以下を実施。

2. **GOOGLE_CLOUD_PROJECT の設定（どれか一つ）**

   **A. mcp.json で指定する（推奨）**  
   `.cursor/mcp.json` の `stitch` に `env` を追加し、実際の Project ID を書く:

   ```json
   "stitch": {
     "command": "npx",
     "args": ["-y", "stitch-mcp"],
     "env": {
       "GOOGLE_CLOUD_PROJECT": "あなたの実際のプロジェクトID"
     }
   }
   ```

   **B. 環境変数で指定する**  
   - Windows: システムの環境変数に `GOOGLE_CLOUD_PROJECT` を追加  
   - または Cursor の設定で環境変数 `GOOGLE_CLOUD_PROJECT` を設定  
   （この場合、mcp.json の `stitch` に `env` を書かなければ、その値が使われます）

3. **gcloud の認証**  
   Project ID を設定しても認証エラーになる場合は、ターミナルで:

   ```bash
   gcloud auth application-default login
   gcloud config set project あなたのプロジェクトID
   ```

4. **Stitch API の有効化**  
   [Google Cloud Console](https://console.cloud.google.com/) → API とサービス → ライブラリ → 「Stitch API」で有効化。

### その他

- **Unauthenticated（未認証）**
  - `gcloud auth application-default login` を再度実行
  - Project ID が正しいか、Stitch API が有効か確認

- **接続できない**
  - ファイアウォールやプロキシの影響がないか確認
  - Cursor の MCP ログでエラー内容を確認

## 参考リンク

- [Stitch、リモートStitch MCPサーバーを発表（gihyo.jp）](https://gihyo.jp/article/2026/01/google-stitch-mcp)
- [Stitch by Google](https://stitch.withgoogle.com/)
- [stitch-mcp (npm)](https://www.npmjs.com/package/stitch-mcp)
