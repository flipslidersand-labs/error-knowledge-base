---
title: "Qdrant K8s probe で /readiness が 404 になる"
tags: [deployment]
severity: high
source: personal
date: "2026-06-29"
---

## 症状

Kubernetes の `readinessProbe` / `livenessProbe` / `startupProbe` に `/readiness` を指定すると
HTTP 404 が返り、Pod が `Terminating` ループに入る。

## 原因

Qdrant は `/readiness` エンドポイントを提供していない。
正しいエンドポイントは以下：

| 用途           | エンドポイント                        |
| -------------- | ------------------------------------- |
| readinessProbe | `/readyz`（全シャード準備完了を確認） |
| livenessProbe  | `/livez`（プロセス生存確認）          |
| startupProbe   | `/livez`                              |
| 総合ステータス | `/healthz`                            |

## 対処

k8s manifest を修正：

```yaml
readinessProbe:
  httpGet:
    path: /readyz # ← /readiness ではない
    port: http

livenessProbe:
  httpGet:
    path: /livez # ← /readiness ではない
    port: http

startupProbe:
  httpGet:
    path: /livez # ← /readiness ではない
    port: http
```

## 確認方法

```bash
curl http://localhost:6333/readyz   # HTTP 200
curl http://localhost:6333/livez    # HTTP 200
curl http://localhost:6333/readiness  # HTTP 404 ← これは使わない
```

## 参考

- Qdrant 公式ドキュメント: https://qdrant.tech/documentation/guides/administration/
- 修正 PR: fix/qdrant-probe-endpoints ブランチ（Issue #92）
