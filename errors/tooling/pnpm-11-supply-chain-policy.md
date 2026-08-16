---
title: "pnpm 11 supply-chain policy で GitHub Actions CI が失敗する"
tags: [tooling, CI]
severity: high
source: personal
date: "2026-07-13"
---

# pnpm 11 supply-chain policy で GitHub Actions CI が失敗する

- **severity**: high
- **category**: tooling / CI
- **date**: 2026-07-13

## 症状

`pnpm install --frozen-lockfile` が以下のエラーで失敗する:

```
ERR_PNPM_MINIMUM_RELEASE_AGE_VIOLATION
Package "foo@1.2.3" was published 3 hours ago.
The publisher policy requires packages to be at least 24 hours old before installation.
```

## 原因

pnpm 11 (latest) は supply-chain attack 対策として `minimumReleaseAge` ポリシーを導入。
公開から24時間以内のパッケージを自動ブロックする。
GitHub Actions の `pnpm/action-setup@v4` に `version: latest` を指定すると pnpm 11 がインストールされる。

## 解決策

`deploy.yml` で pnpm バージョンを `10` に固定する:

```yaml
- uses: pnpm/action-setup@v4
  with:
    version: 10 # 11 はsupply-chain policyでブロックされる
```

`.npmrc` に `minimumReleaseAge=0` を書く方法もあるが、ポリシーをオフにするより pnpm 10 を使う方が安全。

## 予防

新規リポの GitHub Pages CI テンプレートは最初から `version: 10` で固定する。
pnpm メジャーバージョンを上げる際はこのポリシーの影響を確認すること。
