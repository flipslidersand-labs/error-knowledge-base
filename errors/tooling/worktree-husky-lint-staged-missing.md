---
title: "git worktree 内で husky pre-commit が lint-staged not found で失敗"
tags: [worktree, husky, lint-staged, pnpm]
severity: low
source: personal
date: "2026-07-02"
---

## 症状

worktree 内で `git commit` すると
`ERR_PNPM_RECURSIVE_EXEC_FIRST_FAIL Command "lint-staged" not found` で失敗。

## 原因

git worktree は node_modules を共有しない。husky の pre-commit hook は
worktree 側の node_modules から lint-staged を探すため、未インストールだと失敗する。

## 解決策

worktree ルートで一度だけ実行:

```bash
pnpm install --frozen-lockfile
```

pnpm store キャッシュが効くため数秒で完了する。

## 予防

- worktree 作成直後に `pnpm install --frozen-lockfile` をセットで実行する
- `--no-verify` での回避は prettier/black が走らずフォーマット差分が残るので使わない
