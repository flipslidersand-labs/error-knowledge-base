---
title: "ARC runner が別 org のジョブを拾わない（githubConfigUrl スコープ制限）"
tags: [arc, github-actions, kubernetes, runner]
severity: high
source: personal
date: "2026-08-03"
---

## 症状

`runs-on: arc-knowledge-db` の GitHub Actions ジョブが queued のまま実行されない。
ARC listener ログでは `assigned job=0, decision=0` がループし続ける。

## 原因

ARC runner scale set の `githubConfigUrl` は登録先リポジトリ/org を決定する。
`arc-dev-nodee` は `flipslidersand/dev-nodee-infrastructure` に登録されているため、
`yukilabs-core/knowledge-db` のジョブは dispatch されない。

```yaml
# 誤り：flipslidersand 専用ランナーを yukilabs-core ワークフローで指定
runs-on: arc-dev-nodee # -> flipslidersand/dev-nodee-infrastructure にしか届かない
```

さらに `arc-knowledge-db` ランナーを新設しても `githubConfigSecret` に
`yukilabs-core` アクセス可能なトークンが必要（既存の flipslidersand PAT は pull 権限のみ）。

## 解決策

1. `yukilabs-core` 専用シークレットを作成:

```bash
YUKI_TOKEN=$(gh auth token --user yukilabs-core)
kubectl create secret generic arc-knowledge-db-github-secret \
  -n arc-runners --from-literal=github_token="${YUKI_TOKEN}"
```

2. ArgoCD Application manifest で専用シークレットを参照:

```yaml
githubConfigSecret: arc-knowledge-db-github-secret
```

3. 全ワークフローの `runs-on` を `arc-knowledge-db` に統一。

## 予防

- org をまたぐ場合は必ず別 runner scale set + 別シークレットを作成する
- `githubConfigUrl` に設定したリポジトリ以外のジョブは絶対に届かない
- runner scale set 登録後に `gh api repos/<org>/<repo>/actions/runners` で確認
  （ARC v2 は旧 API に出ないが 0 なら未登録の可能性あり）
