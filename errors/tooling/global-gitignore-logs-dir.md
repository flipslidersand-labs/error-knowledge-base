---
title: "global gitignore の [Ll]ogs/ がログリポの logs/ をブロックする"
tags: [tooling, git]
severity: medium
source: personal
date: "2026-07-13"
---

# global gitignore の [Ll]ogs/ がログリポの logs/ をブロックする

- **severity**: medium
- **category**: tooling / git
- **date**: 2026-07-13

## 症状

```
error: The following paths are ignored by one of your .gitignore files:
logs
hint: Use -f if you really want to add them.
```

`git add logs/` が通らない。`.gitignore` に `logs/` を追加してもエラーが変わらない。

## 原因

`~/.gitignore_global` に Unity 由来の `[Ll]ogs/` パターンが含まれている。
グローバル gitignore はリポ内の `.gitignore` より優先されるのではなく、
**リポ内の `.gitignore` の override (`!logs/`) が効かない**ことが問題。

実際には `core.excludesFile` 経由のグローバル無視と、リポ内の `!pattern` の関係:
グローバルで無視されたパスはリポ内 `.gitignore` の `!` で復活させることができる。

## 解決策

各ログリポに `.gitignore` を作成し、明示的に un-ignore する:

```gitignore
# global gitignore [Ll]ogs/ を override
!/logs/
!logs/
```

両方書かないと効かない場合があるため両方追加する。

## 予防

logs/ ディレクトリを git 管理するリポを新規作成する際は最初にこの `.gitignore` を追加する。
