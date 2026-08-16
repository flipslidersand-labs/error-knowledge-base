---
title: "pnpm workspace 未登録サブディレクトリで install が効かない"
tags: [pnpm, workspace, node_modules]
severity: medium
source: personal
date: "2026-07-04"
---

## 症状

`pnpm-workspace.yaml` に未登録のサブディレクトリ（例: `scripts/gmail-mcp/`）で
`pnpm install` を実行しても、ローカルに `node_modules/` が作られない。
ルートの workspace install が走るだけで依存が解決されない。

## 原因

pnpm はサブディレクトリで実行しても、親ディレクトリに `pnpm-workspace.yaml` があれば
そのルートに対して install を実行する。
`pnpm-workspace.yaml` の `packages: []`（空リスト）でも同様で、
対象ディレクトリが workspace メンバーでなければパッケージはインストールされない。

`.npmrc` に `ignore-workspace=true` を追加しても **効果なし**（pnpm v10 時点）。

## 解決策

workspace 外のスタンドアロンスクリプトには `npm install` を使う：

```bash
cd scripts/gmail-mcp
npm install
```

または pnpm を使いたい場合は `pnpm-workspace.yaml` に追加する：

```yaml
packages:
  - "scripts/gmail-mcp"
```

## 予防

- `scripts/` 配下にスタンドアロン Node.js スクリプトを置く場合は `npm install` を使う
- husky などの prepare hook が workspace 全体に干渉するため、`--ignore-scripts` も検討
