---
title: "Sakura VPS の Vault は Docker 内にあり、ホストに vault バイナリがない"
tags: [vault, sakura-vps, docker]
severity: medium
source: personal
date: "2026-07-08"
---

## 症状

SSH で Sakura VPS に入り `vault kv get ...` を実行すると `vault: command not found` が出る。

## 原因

VPS ホストには vault バイナリがインストールされていない。
Vault は `vault-server` という Docker コンテナとして稼働しており、コンテナ内にのみバイナリがある。

## 解決策

```bash
ssh ubuntu@os3-369-17699.vs.sakura.ne.jp \
  "docker exec vault-server env \
    VAULT_ADDR=http://127.0.0.1:8200 \
    VAULT_TOKEN=<token> \
    vault kv get secret/infra/discord-test"
```

トークンは gopass から取得:

```bash
ROOT_TOKEN=$(gopass show cloud/sakura/vault/root-token)
```

## 予防

- SSH 後に `which vault` で確認する前に、まず `docker ps | grep vault` でコンテナ確認
- `minipc-token` は権限が限定的（403 になる場合あり）。管理操作は `root-token` を使う
- ローカルから SSH トンネル経由で Vault に接続したい場合:
  ```bash
  ssh -L 8200:localhost:8200 ubuntu@os3-369-17699.vs.sakura.ne.jp -N &
  export VAULT_ADDR=http://127.0.0.1:8200
  vault kv get secret/infra/...
  ```
