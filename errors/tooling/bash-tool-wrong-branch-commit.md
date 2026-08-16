---
title: "bash tool で git checkout -b 後に別ブランチへ誤コミット"
tags: [git, bash-tool, claude-code]
severity: medium
source: personal
date: "2026-07-16"
---

## 症状

```bash
# Bash call 1
git -C /path/to/repo checkout -b feat/new-feature
# → "Switched to a new branch 'feat/new-feature'"

# Bash call 2（後続の別コール）
git add file.yml && git commit -m "..."
# → コミットが feat/old-branch に行く
```

新しいブランチ `feat/new-feature` に切り替わったはずが、
実際には `feat/old-branch` にコミットされる。

## 原因

Claude Code の Bash ツールはコール間で working directory を持続するが、
`git -C /path` フラグは git コマンドのみに適用される（シェルの cd とは異なる）。
次のコールでは git repository の HEAD が元のブランチのまま残るケースがある。

特に `pnpm issues:start` 等のコマンドを同一 Bash コールに続けると、
pnpm が workspace root に移動することで git の参照先が変わる可能性がある。

## 解決策

誤コミット発覚後の修復手順:

```bash
# 1. 正しいブランチで cherry-pick
git checkout feat/new-feature
git cherry-pick <誤コミットのSHA>

# 2. 元ブランチで revert（reset --hard は禁止）
git checkout feat/old-branch
git revert HEAD --no-edit
git push origin feat/old-branch
```

## 予防

- `git -C /path checkout -b` の直後に `git branch --show-current` で確認する
- ブランチ切り替えと pnpm/npm コマンドは別 Bash コールで実行する
- コミット前に必ず `git branch --show-current` を確認する
