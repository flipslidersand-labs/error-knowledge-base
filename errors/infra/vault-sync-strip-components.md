---
title: "Vault sync — tar --strip-components 数が不足でネストディレクトリが発生"
tags: [infra]
severity: medium
source: personal
---

# Vault sync — tar --strip-components 数が不足でネストディレクトリが発生

## 現象

`vault-standby` が `initialized: false` を返す。
`docker exec vault-standby ls /vault/file/core/` が空。

## 原因

`docker exec vault-server tar -czf - /vault/file` は `/vault/file/core/...` 構造を出力する。

`--strip-components=1` では `vault/file/core/...` が展開先 `/home/yuki/vault/file/` に対して
`/home/yuki/vault/file/file/core/...` になる（`file/` がネスト）。

正しくは `--strip-components=2` で `/home/yuki/vault/file/core/...` になる。

## 修正

```bash
# vault-sync.sh
| tar -xzf - --strip-components=2 -C "${LOCAL_DST}"
# (was --strip-components=1)
```

## 関連

- MINIPC: `/home/yuki/scripts/vault-sync.sh`
- vault-standby は再起動後に手動 unseal が必要（自動 unseal なし）
- unseal keys: `gopass show cloud/sakura/vault/unseal-key-{1,2}`（しきい値 t=2）
