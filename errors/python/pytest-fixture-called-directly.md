---
title: "pytest fixture を直接呼び出すと 'Fixture called directly' エラー"
tags: [pytest, python, fixtures]
severity: low
source: personal
date: "2026-08-16"
---

# pytest: Fixture called directly エラー

## 症状

```
Failed: Fixture "in_memory_db" called directly. Fixtures are not meant to be called directly,
but are created automatically when test functions request them as parameters.
```

## 原因

`@pytest.fixture` で定義した関数を `result = in_memory_db()` のように直接呼び出した。
pytest は fixture をジェネレーター込みで管理するため、直接呼び出しは pytest 7.x 以降で禁止。

## 解決策

テスト関数のパラメーターとして受け取る:

```python
# NG
def test_something():
    conn = in_memory_db()  # 直接呼び出し

# OK
def test_something(in_memory_db):  # pytest が自動注入
    conn = in_memory_db
```

外部パッケージが提供する fixture (`qa_shared.conftest_shared` 等) は
プロジェクトの `conftest.py` で `from qa_shared.conftest_shared import *` として
pytest に認識させる必要がある。

## 予防

- fixture のテストは直接呼び出しで動作確認しようとしない
- パッケージ提供 fixture は必ず `conftest.py` で re-export する
