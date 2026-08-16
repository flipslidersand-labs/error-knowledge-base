---
title: "ARC runner label のスコープ分離（personal repo）"
tags: [infra]
severity: medium
source: personal
---

# ARC runner label のスコープ分離（personal repo）

## 発生日

2026-08-02

## 症状

`dev-infrastructure` の CI が `runs-on: arc-dev-nodee` を指定しているのに、ジョブが永続的に `queued` のまま処理されない。

## 根本原因

GitHub personal account では runner はリポジトリレベルでスコープが分離される。

- `arc-dev-nodee` = `dev-nodee-infrastructure` に登録された ARC scale set
- `dev-infrastructure` のジョブは `dev-infrastructure` に登録された runner しか処理できない
- `dev-infrastructure` に登録されている runner のラベルは `arc-dev-pc`

## 確認方法

```bash
# リポジトリに登録されている runner のラベルを確認
gh api repos/flipslidersand/dev-infrastructure/actions/runners \
  --jq '.runners[] | {name: .name, labels: [.labels[].name]}'
```

## 修正

`dev-infrastructure` の全 workflow の `runs-on: arc-dev-nodee` → `runs-on: arc-dev-pc` に変更。

```bash
find .github/workflows/ -name "*.yml" -exec \
  sed -i 's/runs-on: arc-dev-nodee/runs-on: arc-dev-pc/g' {} \;
```

## 関連

- PR #330: https://github.com/flipslidersand/dev-infrastructure/pull/330
