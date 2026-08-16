---
title: "PR/コミットの close キーワードで複数 Issue を並べても先頭しか閉じない"
tags: [github, pr, issue, auto-close, gotcha]
severity: medium
source: personal
date: "2026-08-17"
---

# PR/コミットの close キーワードで複数 Issue を並べても先頭しか閉じない

## 症状

`close #2 #3 #4 #5 #6 #7` と書いたコミットで PR を default ブランチにマージしたが、
自動クローズされたのは **#2 だけ**。#3-#7 は OPEN のまま残った。
PR 本文の `Closes #2, #3, #4, #5, #6, #7` でも同様に先頭しか閉じない。

## 原因

GitHub の Issue 自動クローズは **「キーワード + 単一の Issue 番号」** のペアしか解釈しない。
1 つのキーワードに番号をスペース区切り・カンマ区切りで並べても、後続の番号は
プレーンな参照（リンク）として扱われ、クローズ対象にならない。

## 解決策

各 Issue 番号に対してキーワードを繰り返す。

```text
Closes #2
Closes #3
Closes #4
```

取りこぼした場合は手動クローズで復旧できる。

```bash
for n in 3 4 5 6 7; do
  gh issue close $n --repo <owner>/<repo> --reason completed \
    --comment "PR #9 で対応済み（自動クローズ漏れの手動対応）"
done
```

## 予防

- PR 本文/コミットで複数 Issue を閉じるときは **1 番号ごとにキーワードを書く**
- マージ後は必ず対象 Issue の state を確認する（`gh issue view <n> --json state`）
- 対応: `Closes #2, #3` / `close #2 #3` は NG、`Closes #2` を行ごとに列挙が正
