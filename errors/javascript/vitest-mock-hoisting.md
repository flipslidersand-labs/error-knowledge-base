---
title: "vi.mock ファクトリ内で外部変数を参照できない"
tags: [vitest, mocking, hoisting]
severity: medium
source: personal
date: "2026-06-17"
---

# 症状

```
Error: [vitest] There was an error when mocking a module.
Caused by: ReferenceError: Cannot access 'mockFoo' before initialization
```

# 原因

`vi.mock()` はファイル先頭にホイストされる。
そのため、ファクトリ関数内で `const mockFoo = { ... }` のような変数を参照すると、
変数の初期化より前に実行されて ReferenceError になる。

# 解決策

`vi.hoisted()` でモックオブジェクトを事前定義する。

```js
// ❌ 動かない
const mockFoo = { bar: vi.fn() };
vi.mock("../foo.js", () => ({ default: mockFoo }));

// ✅ 正しい
const { mockFoo } = vi.hoisted(() => ({ mockFoo: { bar: vi.fn() } }));
vi.mock("../foo.js", () => ({ default: mockFoo }));
```

# 予防

ルートテスト変数を `vi.mock` ファクトリが参照する場合は必ず `vi.hoisted()` を使う。
