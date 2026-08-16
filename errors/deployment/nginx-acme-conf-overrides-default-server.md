---
title: "nginx: acme.conf の server_name 指定ブロックが default_server より優先され 301 リダイレクトが効かない"
tags: [nginx, docker, sakura-vps, https]
severity: medium
source: personal
date: "2026-08-03"
---

## 症状

`webhook.conf` に `listen 80 default_server` + `location / { return 301 https://...; }` を設定したが、
`http://<vps-hostname>/health` が 301 ではなく 404 を返す。

## 原因

`acme.conf` が同じホスト名（`server_name os3-369-17699.vs.sakura.ne.jp`）で `listen 80` を持っており、
nginx の優先順位で `server_name` 完全一致ブロックが `default_server` より先にマッチする。
`acme.conf` には `location /` が無いため、`/health` は 404 になっていた。

## 解決策

`acme.conf`（ホスト名指定の HTTP ブロック）に `location /` の 301 リダイレクトを追加：

```nginx
server {
    listen 80;
    server_name os3-369-17699.vs.sakura.ne.jp;

    location /.well-known/acme-challenge/ {
        root /var/www/acme-webroot;
        default_type text/plain;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}
```

## 予防

nginx で HTTP→HTTPS リダイレクトを設定する際、`default_server` だけでなく
**そのホスト名を明示する全ての server ブロック**にリダイレクトを入れる。
`nginx -T | grep -A5 'server_name <hostname>'` で重複ブロックを事前確認する。
