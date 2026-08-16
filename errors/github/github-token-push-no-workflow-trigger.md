---
title: "GITHUB_TOKEN の bot push は workflow を起動せず required checks が付かない"
tags: [github-actions, branch-protection, auto-fix]
severity: medium
source: personal
date: "2026-07-04"
---

## 症状

PR の required checks（build/lint/test/type-check）が成功しているのに
「the base branch policy prohibits the merge」でマージ不可。

## 原因

Auto Fix workflow が GITHUB_TOKEN で整形コミットを push → head SHA が進む。
GitHub の再帰防止仕様により **GITHUB_TOKEN で作られた push は
workflow を起動しない**ため、新 head に check-run が一切付かない。

## 解決策

自分のトークンで empty commit を push して CI を再発火:

```bash
# Git Data API: 同じ tree を指す empty commit を作って ref を進める
gh api -X POST .../git/commits -f message="chore: CI 再発火" -f tree=$TREE -f "parents[]=$HEAD"
gh api -X PATCH .../git/refs/heads/<branch> -f sha=$NEW
```

恒久対策は Issue #167（auto-fix の push を PAT 化）。

## 予防

- required checks が「無い」のと「失敗」は区別する。
  `gh api .../commits/<head_sha>/check-runs` で head に付いた check-run を直接見る
- bot が push する workflow を作るときは、後続 CI の発火まで設計に含める
