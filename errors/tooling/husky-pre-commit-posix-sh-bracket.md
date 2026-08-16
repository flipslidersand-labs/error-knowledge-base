---
title: "husky pre-commit hook で [[ ]] を使うと /bin/sh 環境でエラーになる"
tags: [husky, bash, sh, hook]
severity: medium
source: personal
date: "2026-08-09"
---

## 症状

```
.husky/pre-commit: 6: [[: not found
```

commit は通るが警告が出る。

## 原因

husky v9 の hook は `/bin/sh` で実行される。`[[` は bash 拡張で POSIX sh には存在しない。

## 対策

`[[` の代わりに `case` 文または `[` (単括弧) を使う。

```bash
# NG (bash only)
if [[ "$CWD" == "$REPO_ROOT" ]]; then ...

# OK (POSIX sh)
if [ "$CWD" = "$REPO_ROOT" ]; then ...

# NG (bash only, パターンマッチ)
if [[ "$CWD" == "$WORKTREE_DIR"* ]]; then ...

# OK (POSIX sh, パターンマッチ)
case "$CWD" in
  "$WORKTREE_DIR"*) : ;;
  *) echo "警告" ;;
esac
```

## 関連

- #757 pre-commit hook 実装
- PR #758
