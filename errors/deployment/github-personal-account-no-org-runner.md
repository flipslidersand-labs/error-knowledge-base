---
title: "GitHub個人アカウントはorg-level self-hosted runner登録不可（404）"
tags: [github-actions, arc, self-hosted-runner, organization]
severity: high
source: personal
date: "2026-08-01"
---

## 症状

ARC (Actions Runner Controller) の `githubConfigUrl` を
`https://github.com/<username>` (個人アカウント) に変更したところ、
AutoscalingListener が以下のエラーでcrash loopした。

```
failed to create runner registration token
POST https://api.github.com/orgs/flipslidersand/actions/runners/registration-token
→ 404 Not Found
```

## 原因

GitHub の self-hosted runner registration token エンドポイントは
`/orgs/{org}` パスを使うが、個人アカウント (`flipslidersand`) は
GitHub Organization ではないため404が返る。

個人アカウントがサポートするのはリポジトリレベルのランナーのみ
(`/repos/{owner}/{repo}/actions/runners/registration-token`)。

## 解決策

1. `githubConfigUrl` をリポジトリレベルに戻す:

   ```yaml
   githubConfigUrl: https://github.com/flipslidersand/dev-infrastructure
   ```

2. crash loopしたARC resourcesをすべて削除してArgoCD再作成を待つ:
   ```bash
   kubectl delete autoscalinglisteners -n arc-runners --all
   # finalizer が残る場合
   kubectl patch autoscalinglistener <name> -n arc-runners \
     -p '{"metadata":{"finalizers":[]}}' --type=merge
   kubectl delete autoscalingrunnerset arc-dev-nodee -n arc-runners --ignore-not-found
   # ArgoCD が自動再作成（selfHeal: true）
   ```

## 予防

- org-level ARC runner には **GitHub Organization** アカウントが必要
- 個人アカウントで org-level 移行を計画している場合は
  先に Organization を作成してから PAT スコープ `manage_runners:org` で設定する
- PAT には `Administration RW` + `manage_runners:org` の両方が必要
