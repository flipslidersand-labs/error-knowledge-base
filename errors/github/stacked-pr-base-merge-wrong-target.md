---
title: "stacked PR を base 未確認でマージし master に入らなかった（PR #148）"
tags: [github, pr, merge, stacked-pr]
severity: high
source: personal
date: "2026-07-04"
---

## 症状

`gh pr merge 148` が成功し Issue も自動クローズされたのに、変更が master に無い。

## 原因

PR #148 の base が `feat/discord-phase3e`（stacked PR）だった。base の PR #147 を
マージではなく **close** したため GitHub の自動 retarget が働かず、base が
feature ブランチのまま残っていた。マージは成功したが行き先が master ではなかった。

## 解決策

master から新ブランチを切り、必要ファイルを Git Data API で単一コミット化して
別 PR（#166）として復旧マージ。

## 予防

- マージ前に必ず base を確認する: `gh pr view <n> --json baseRefName`
- stacked PR の親を close する場合、子 PR の base を手動で retarget する:
  `gh pr edit <n> --base master`
- 「MERGED = master に入った」ではない。マージ後は
  `git merge-base --is-ancestor <merge_commit> origin/master` で確認できる
