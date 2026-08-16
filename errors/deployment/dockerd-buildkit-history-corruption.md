---
title: "dockerd クラッシュループ: BuildKit history DB 破損"
tags: [deployment]
severity: medium
source: personal
---

# dockerd クラッシュループ: BuildKit history DB 破損

## 症状

`docker.service` が起動直後に `fatal error: fault`（SIGSEGV）でクラッシュ。
systemd が 4 回再起動を試みて "Start request repeated too quickly" で諦める。
`sudo docker ps` は "Cannot connect to the Docker daemon"。全コンテナ停止。

## 診断手順

1. `systemctl status docker` → failed / restart 上限到達
2. `sudo dockerd --validate` → configuration OK（設定は無実）
3. `dmesg | grep -iE 'mce|oom|segfault'` → ハードウェア/メモリ異常なし
4. `dpkg -l | grep docker` → パッケージ整合（部分アップグレードなし）
5. `systemctl is-active containerd` → active（containerd は無実）
6. **完全なスタックトレースを取得**（stderr を捕捉）:
   ```bash
   sudo bash -c 'timeout 25 dockerd > /root/dockerd-crash.log 2>&1'
   sudo sed -n '/fatal error: fault/,+80p' /root/dockerd-crash.log
   ```

## 根本原因

スタックトレースが指す:
```
moby/buildkit/solver/llbsolver/history.(*Queue).clearOrphans
  → go.etcd.io/bbolt (buildhistory.go:211)
  → protobuf decode → unicode/utf8.Valid → sigpanic (fault)
```

= **BuildKit の build history DB (bbolt) 内の protobuf レコードが破損**。
dockerd 起動時に BuildKit が history を読んで orphan 掃除する際、
壊れた UTF-8 文字列を検証してメモリ不正アクセス → daemon 全体がクラッシュ。

DB: `/var/lib/docker/buildkit/history_c8d.db`

## 解決策（データ損失なし）

build history は使い捨てデータ。破損 DB を退避するだけで復旧:

```bash
sudo systemctl stop docker docker.socket
sudo mv /var/lib/docker/buildkit/history_c8d.db \
        /var/lib/docker/buildkit/history_c8d.db.corrupt
sudo systemctl reset-failed docker.service docker.socket
sudo systemctl start docker
```

BuildKit が空の history DB を再生成する。**イメージ/コンテナ/volume は一切失われない**。

## 誤診に注意（遠回りした点）

- containerd `meta.db` リセットは**無効**（containerd は無実）。触る前にスタックトレースで
  faulting subsystem を特定すること。
- コンテナ metadata の退避も無関係だった。

## 教訓

`fatal error: fault` は必ず **完全なスタックトレースの faulting goroutine** を読む。
protobuf/utf8 の fault は bbolt に格納された破損レコードのデコードが典型。
