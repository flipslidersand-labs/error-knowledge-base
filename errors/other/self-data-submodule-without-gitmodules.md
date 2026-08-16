---
title: "self-data が .gitmodules なしのサブモジュールとして記録されCI全失敗"
tags: [git, submodule, ci, gitignore]
severity: high
source: personal
date: "2026-08-16"
---

# git: .gitmodules なしのサブモジュールで CI 全ジョブ失敗

## 症状

CI の全ジョブが以下で失敗。

```
fatal: no submodule mapping found in .gitmodules for path 'self-data'
exit code 128
```

gitleaks / actionlint / auto-fix の全ジョブが同時にコケた。

## 原因

auto-commit hook が `self-data/`（独立した git リポジトリ）を誤って `git add` し、
`.gitmodules` エントリなしのサブモジュールとして commits に記録してしまった。

## 解決策

```bash
git rm --cached self-data
```

その後 `.gitignore` に `/self-data/` を追加してコミット。

## 予防

- 独立 git リポジトリを持つディレクトリは事前に `.gitignore` に登録する
- auto-commit hook がある場合は `git status` で `self-data` が含まれていないか確認してから実行
