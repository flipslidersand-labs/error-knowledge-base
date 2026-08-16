---
title: "GitHub Actions spending limit超過時はself-hostedランナーも含め全ジョブがブロックされる"
tags: [github-actions, billing, spending-limit, self-hosted-runner]
severity: high
source: personal
date: "2026-08-01"
---

## 症状

GitHub Actions の無料枠 (2,000 min/月) を使い切った後、
spending limit が $0 (デフォルト) の状態だと、
**self-hosted runner を指定したジョブも含めて全ワークフローが queued のまま実行されない。**

ARC runner は正常稼働しているのにジョブが割り当てられない。

## 原因

GitHub は spending limit 超過時に請求防止のため **全ワークフローをブロック** する。
self-hosted runner は GitHub-hosted と異なりコンピュート費用はかからないが、
ジョブのキューイング・配信・ログ記録には GitHub インフラが必要で、
その処理も制限対象になる。

## 解決策

GitHub Settings → Billing & plans → Spending limits で
Actions の spending limit を $1 以上に設定する。

直接 URL: `https://github.com/settings/billing/spending_limit`

月の上限を制限したい場合は $1〜$5 などの低い値に設定しておくと
予期しない大量課金を防ぎつつ self-hosted runner が使えるようになる。

月初 (1日) に請求サイクルがリセットされるとブロックが解除される。

## 予防

- 無料枠消費が多いリポジトリの CI は self-hosted runner (`GATE_RUNNER` 変数) に移行する
- spending limit は $0 ではなく $1〜$5 に設定しておく
- 月の使用量は `https://github.com/settings/billing` で確認できる
- 消費量が多いリポジトリを特定: GitHub API `GET /repos/{owner}/{repo}/actions/cache/usage` や billing API で分析する
