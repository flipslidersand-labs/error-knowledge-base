---
title: "ARC: user-level githubConfigUrl で listener pod が 404 エラー"
tags: [kubernetes, helm, arc, github-actions, ci]
severity: medium
source: personal
project: dev-infrastructure
env: "ARC 0.14.2 (gha-runner-scale-set chart), k3s"
os: Linux
date: "2026-08-14"
---

# ARC runner scale set: user-level githubConfigUrl で 404

## 症状

```
error: failed to get runner registration token on refresh:
  request POST https://api.github.com/orgs/<username>/actions/runners/registration-token
  failed(status="404 Not Found")
```

AutoscalingRunnerSet の listener pod が起動しない。

## 原因

`githubConfigUrl: https://github.com/<username>` (user/org-level) を指定すると、
ARC 0.14.2 が `/orgs/<username>/actions/runners/registration-token` API を叩く。
個人アカウント（Organization 未作成）の場合、`/orgs/` エンドポイントは 404。

GitHub は user-level self-hosted runner を `/user/runners` で提供しているが、
ARC 0.14.2 はこのエンドポイントを使わず `/orgs/` に固定している。

## 解決策

`githubConfigUrl` を **repo-level** に変更する:

```yaml
githubConfigUrl: https://github.com/<username>/<repo-name>
```

runner は指定リポジトリ専用になる。複数リポジトリで共有するには、
Organization を作成して org-level URL を使うか、各リポジトリにrunnerを登録する。

## 回避策

Organization を作成し、org-level URL (`https://github.com/<org>`) を使う。
org スコープ runner は全リポジトリで共有可能。

## 関連

- ARC version: 0.14.2 (gha-runner-scale-set chart)
- Epic #854 CI Compute Platform
