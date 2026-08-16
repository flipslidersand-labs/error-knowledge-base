---
title: "pytest の path 部分文字列判定が worktree 名に誤マッチして全テスト skip"
tags: [pytest, worktree, conftest]
severity: medium
source: personal
date: "2026-07-02"
---

## 症状

`pytest_collection_modifyitems` で integration テストだけを skip するつもりが、
unit テストを含む **全 32 テストが skip** された。

## 原因

判定が `"integration" in str(item.fspath)` という部分文字列マッチだったため、
git worktree のパス `.claude/worktrees/discord-138-integration/...` に含まれる
"integration" に全テストファイルがマッチした。

## 解決策

conftest.py 自身のディレクトリを基準にした前方一致に変更:

```python
INTEGRATION_DIR = os.path.dirname(os.path.abspath(__file__))
# ...
if str(item.fspath).startswith(INTEGRATION_DIR):
    item.add_marker(skip)
```

## 予防

- テストの選別はパスの部分文字列でなく `os.path.dirname(__file__)` 基準か
  marker ベース（`item.get_closest_marker`）で行う
- worktree 分離運用ではディレクトリ名が任意の文字列を含む前提でコードを書く
