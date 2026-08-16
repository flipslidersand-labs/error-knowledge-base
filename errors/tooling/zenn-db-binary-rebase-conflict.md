---
title: "zenn-content の db/zenn.db がリベース時にバイナリコンフリクト"
tags: [git, zenn, binary-file]
severity: low
source: personal
date: "2026-07-07"
---

## 症状

`git pull --rebase origin main` 後に `db/zenn.db` でコンフリクト。
自動マージ不可（バイナリファイルのため）。

```
CONFLICT (content): Merge conflict in db/zenn.db
```

## 原因

`db/zenn.db` は Zenn 自動ジョブ（trending keywords fetch）が定期更新するバイナリ。
ローカルに stash していた変更と競合した。

## 解決策

リモート版を採用する（ローカルの zenn.db 変更は通常不要）:

```bash
git checkout --theirs db/zenn.db
git add db/zenn.db
```

## 予防

zenn-content での作業前に `git pull` を先に実行する。
または `db/zenn.db` を .gitignore に加えることを検討（自動ジョブが管理するファイルのため）。
