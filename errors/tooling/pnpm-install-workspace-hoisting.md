---
title: "pnpm install が親の pnpm-workspace.yaml に引っ張られてサブディレクトリで正しく動かない"
tags: [pnpm, workspace, ci]
severity: medium
source: personal
date: "2026-08-03"
---

## 症状

`yukilabs-core/knowledge-db` で `pnpm install --no-frozen-lockfile` を実行すると
`../.. prepare: Done` と出て 771ms で終わる。`pnpm-lock.yaml` が更新されない。

CI で `ERR_PNPM_OUTDATED_LOCKFILE` が発生し、lockfile の specifiers が package.json と不一致になる。

## 原因

`/home/dev-nodee/projects/pnpm-workspace.yaml`（Platform リポジトリ）が空でも存在するため、
サブディレクトリで `pnpm` を実行するとワークスペースルートとして認識され、
サブディレクトリの `package.json` ではなくルートの install が走る。

## 解決策

```bash
CI=true pnpm install --no-frozen-lockfile --ignore-workspace
```

`--ignore-workspace` フラグで親ワークスペースを無視して単体パッケージとして install できる。
`CI=true` は `confirmModulesPurge` の TTY チェックを回避するために必要。

## 予防

- Platform リポジトリ配下のサブプロジェクトで pnpm を使う場合は必ず `--ignore-workspace` を付ける
- CI スクリプト・Makefile にあらかじめ記載しておく
