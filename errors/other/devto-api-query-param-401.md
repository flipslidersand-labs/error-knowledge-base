---
title: "Dev.to API: クエリパラメータ付きで401、なしで200"
tags: [devto, api, curl]
severity: low
source: personal
date: "2026-08-06"
---

## 症状

```bash
curl -s -H "api-key: ..." "https://dev.to/api/articles/me?per_page=30"
# → {"error": "unauthorized", "status": 401}

curl -s -H "api-key: ..." "https://dev.to/api/articles/me"
# → [{...articles...}]  (200 OK)
```

## 原因

詳細不明。CDN（Varnish）のキャッシュが `Vary: X-Loggedin` ヘッダを含むため、
クエリパラメータの有無でキャッシュキーが分かれ、パラメータ付きのパスに
認証なしのキャッシュが残っていた可能性。

## 解決策

クエリパラメータなしで叩く。デフォルトは30件返るので実用上は問題なし。

## 予防

Dev.to APIはVarnish CDN経由のため、クエリパラメータ付きで401が出たら
まずパラメータなしで試す。
