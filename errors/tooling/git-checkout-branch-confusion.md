---
title: "git checkout -b 後も別ブランチにコミットされた"
tags: [tooling]
severity: medium
source: personal
date: "2026-07-18"
---

## 症状

```bash
git checkout main && git checkout -b docs/vertex-ai-cost-56
# → "branch created" と出力された
# → git commit 後に git branch --show-current が feat/paths-filter-159 を返す
```

コミットログの先頭が `[feat/paths-filter-159 xxx]` となり、別ブランチに乗った。

## 原因

複数の Bash ツール呼び出しを分けたセッション中、`git checkout main` の実行が別ディレクトリ
（または worktree）上で走り、`git checkout -b docs/vertex-ai-cost-56` が意図通りに
切り替わらないまま「branch created」と表示された可能性。もしくは前の Bash セッションの
カレントディレクトリが別 repo になっていたため、checkout が違うリポジトリに対して
実行された。

## 修正手順

1. 誤ったブランチから `git revert <commit-hash>` でロールバック（`git reset --hard` は禁止）
2. `git checkout main && git checkout -b <correct-branch>` で改めてブランチを作る
3. `git cherry-pick <commit-hash>` で正しいブランチにコミットを移植
4. 古い誤ったリモートブランチを `git push origin --delete <bad-branch>` で削除

## 予防策

- `git commit` 直前に必ず `git branch --show-current` で現在ブランチを確認する
- `git checkout` 後に即 `git status` を実行して期待するブランチになっているか確認する
- 複数 Bash 呼び出しを連続させるとき `cd /path/to/repo && git checkout ...` で
  リポジトリを明示的に指定する
