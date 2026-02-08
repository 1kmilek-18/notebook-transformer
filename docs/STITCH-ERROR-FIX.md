# Stitch MCP「Error - Show Output」の解消方法

## よくある原因と対処

### 1. Project ID 未設定

未設定だと `Project ID not found. Set GOOGLE_CLOUD_PROJECT env var` となります。→ 下記「方法2」で mcp.json に記載。

### 2. 認証エラー（アクセストークン取得失敗）

Project ID を設定してもエラーになる場合、ログに次のように出ます。

- `Failed to get access token`
- `Authentication failed. Run: gcloud auth application-default login`

**原因**: Google Cloud の「アプリケーションのデフォルト認証情報」が設定されていません。**Cursor を動かしている PC（Windows なら Windows 上）で** gcloud のログインが必要です。

**対処（WSL / Linux で Cursor を使っている場合）:**

1. **gcloud CLI をインストール**（未導入なら）  
   - **WSL / Linux（snap あり）**: ターミナルで:
     ```bash
     sudo snap install google-cloud-cli --classic
     ```
   - 別の方法: [公式インストール手順](https://cloud.google.com/sdk/docs/install) の「Linux」を参照。

**対処（Windows で Cursor を使っている場合）:**

1. **gcloud CLI を Windows にインストール**（未導入なら）  
   https://cloud.google.com/sdk/docs/install  
   「Windows」用のインストーラでセットアップ。

2. **PowerShell または CMD を開き**、次を実行:
   ```bash
   gcloud auth application-default login
   ```
   ブラウザが開くので、Stitch に使う Google アカウントでログイン。

3. **プロジェクトとクォータを指定**（任意だが推奨）:
   ```bash
   gcloud config set project gen-lang-client-0725514999
   gcloud auth application-default set-quota-project gen-lang-client-0725514999
   ```
   （プロジェクト ID はあなたのものに置き換えてください。）

4. **Cursor を再起動**し、MCP の Stitch をオフ→オンにする。

これで「アプリケーションのデフォルト認証情報」が Windows に保存され、Stitch MCP から利用されます。

## 対処（どちらか一方でOK）

### 方法1: 環境変数で指定（推奨）

1. **実際の Project ID を用意**  
   [Google Cloud Console](https://console.cloud.google.com/) → プロジェクト選択 → プロジェクト ID をコピー

2. **環境変数 `GOOGLE_CLOUD_PROJECT` を設定**
   - **Windows**: システムの環境変数に `GOOGLE_CLOUD_PROJECT` = プロジェクトID を追加し、Cursor を**再起動**
   - **Mac/Linux**: ターミナルで `export GOOGLE_CLOUD_PROJECT=あなたのプロジェクトID` を実行してから Cursor を起動

3. **認証**（未実施なら）  
   ターミナルで:
   ```bash
   gcloud auth application-default login
   gcloud config set project あなたのプロジェクトID
   ```

### 方法2: mcp.json で直接指定

`.cursor/mcp.json` の `stitch` を次のようにします（`あなたのプロジェクトID` を実際の ID に置き換え）:

```json
"stitch": {
  "command": "npx",
  "args": ["-y", "stitch-mcp"],
  "env": {
    "GOOGLE_CLOUD_PROJECT": "あなたのプロジェクトID"
  }
}
```

保存後、Cursor の MCP 一覧で Stitch をオフ→オンにするか、Cursor を再起動してください。

## 補足

- Stitch API を有効化していない場合は [Google Cloud Console](https://console.cloud.google.com/) → API とサービス → ライブラリ → 「Stitch API」で有効化
- 詳細は [MCP-STITCH-SETUP.md](./MCP-STITCH-SETUP.md) を参照
