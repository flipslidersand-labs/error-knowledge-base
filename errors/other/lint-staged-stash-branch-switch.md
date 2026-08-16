---
title: "lint-staged の stash/pop サイクルがブランチを切り替える"
tags: [git, lint-staged, husky, pre-commit]
severity: medium
source: personal
date: "2026-08-16"
---

# lint-staged: stash/pop でブランチが意図せず切り替わる

## 症状

`feat/doc-ingest-pipeline` ブランチでコミット後、カレントブランチが
`perf/round11-optimizations` に戻っていた。
その後 `ls scripts/doc_ingest/` が `__pycache__` しか表示しない。

## 原因

lint-staged の stash 前処理・pop 後処理がブランチ情報を失い、
異なるブランチに checkout する既知のバグ (lint-staged Issue #91 参照)。

## 解決策

影響を受けたブランチのファイルは `git show <branch>:<path>` で参照する:

```bash
git show feat/doc-ingest-pipeline:scripts/doc_ingest/cli.py
```

根本修正は lint-staged のバージョンアップまたは別 hook 方式への移行。

## 予防

コミット直後は `git branch --show-current` で正しいブランチにいるか確認する。
