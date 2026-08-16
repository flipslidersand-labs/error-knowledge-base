---
title: "pnpm issues:close が cwd に関係なく Platform リポの Issue に誤爆する"
tags: [pnpm, gh, issue-cmd, platform]
severity: medium
source: personal
date: "2026-08-09"
---

## 症状

fluxion リポで `cd flipslidersand/fluxion && pnpm issues:close --issue=47` を実行したところ、
fluxion#47 ではなく **dev-nodee-infrastructure#47**（無関係な別 Issue・クローズ済み）に
完了コメントが投稿された。

## 原因

`pnpm issues:close` は Platform ルートの package.json スクリプト
（`node scripts/issue-cmd.mjs`）に解決され、pnpm がスクリプトをルートで実行するため
cwd のリポ情報が使われず、既定リポ（Platform）の Issue 番号に対して操作される。

## 解決策

- 誤爆コメントは `gh api -X DELETE repos/<owner>/<repo>/issues/comments/<id>` で削除
- 外部リポの Issue クローズは `Closes #N` を PR に書いてマージ時 auto-close に任せる、
  または `gh issue close N --repo owner/repo` を直接使う

## 予防

- `pnpm issues:start/close` は **Platform リポの Issue 専用**と覚える
- 他リポでは使わない。改善するなら issue-cmd.mjs に `--repo` オプション or
  cwd の git remote から対象リポを自動検出する機能を追加する（Issue 化済み）
