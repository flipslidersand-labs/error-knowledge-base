---
title: "ArgoCD selfHeal が kubectl patch を即座に revert する"
tags: [argocd, kubernetes, selfheal, gitops]
severity: medium
source: personal
date: "2026-08-01"
---

## 症状

`kubectl patch` や `kubectl edit` で ArgoCD 管理下のリソースを変更しても、
数秒〜数十秒後に ArgoCD が自動的に git の状態に戻してしまう。

```bash
kubectl patch application arc-runner-set -n argocd \
  --type merge -p '{"spec":{"source":{"helm":{"values":"githubConfigUrl: ..."}}}}'
# → ArgoCD が即 revert → 変更が消える
```

## 原因

ArgoCD Application に `selfHeal: true` が設定されている場合、
クラスタ上のリソースと git の状態に差分が生じると自動同期して git 側に戻す。
これは GitOps の正常動作。

## 解決策

変更を反映させるには **git リポジトリ側を更新してマージ** する。

1. 対象ファイルを編集してコミット・push:

   ```bash
   # 例: arc-runner-set.yaml を編集
   git add k8s/argocd/apps/arc-runner-set.yaml
   git commit -m "fix: update githubConfigUrl"
   git push
   ```

2. ArgoCD は `targetRevision: main` をウォッチしているため、
   main ブランチへのマージ後に自動同期される。

3. 緊急で即時反映が必要な場合は ArgoCD UI / CLI で手動 Sync:
   ```bash
   argocd app sync arc-runner-set
   ```
   ただし selfHeal で git state に戻る前提で設計すること。

## 予防

- ArgoCD 管理リソースは直接 kubectl で変更しない運用を徹底する
- `selfHeal: true` のアプリは「kubectl で変えてもすぐ消える」と認識する
- 一時的なデバッグ変更も PR を立てて検証する（ブランチ push → ArgoCD dev env で確認）
