#!/usr/bin/env bash
# Stitch API をこのプロジェクトの GCP で有効化します。
# 事前に以下を実行してください:
#   gcloud auth login
#   gcloud auth application-default login
set -e
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-gen-lang-client-0725514999}"
echo "Enabling Stitch API for project: $PROJECT_ID"
gcloud services enable stitch.googleapis.com --project="$PROJECT_ID"
gcloud auth application-default set-quota-project "$PROJECT_ID" 2>/dev/null || true
echo "Done. Stitch API is enabled."
