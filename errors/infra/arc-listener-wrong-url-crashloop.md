---
title: "ARC AutoscalingListener が誤 URL で CrashLoop → ジョブ詰まり"
tags: [infra]
severity: medium
source: personal
---

# ARC AutoscalingListener が誤 URL で CrashLoop → ジョブ詰まり

## 発生日

2026-08-02

## 症状

- `arc-runners` にランナーポッドが起動しない
- GitHub broker が `assigned job=0` を返し続ける
- 多数のジョブが長時間 `queued` のまま

## 根本原因

`arc-systems` namespace に2つの `AutoscalingListener` が混在していた。

| リソース名                        | githubConfigUrl                              | 状態      |
| --------------------------------- | -------------------------------------------- | --------- |
| `arc-dev-nodee-674c8dbc-listener` | `flipslidersand/dev-nodee-infrastructure` ✅ | Running   |
| `arc-dev-nodee-69c49dfd-listener` | `flipslidersand/dev-infrastructure` ❌       | CrashLoop |

クラッシュしている listener が ARC controller のリソースを消費し、正常な listener のスケーリングを阻害していた。

## 調査コマンド

```bash
kubectl get autoscalinglisteners -n arc-systems
kubectl logs -n arc-systems <listener-pod> --tail=20
```

## 修正

```bash
kubectl delete autoscalinglistener arc-dev-nodee-69c49dfd-listener -n arc-systems
```

削除後、即座にランナーポッドが起動した。

## 予防策

- ARC helm upgrade 後に `kubectl get autoscalinglisteners -n arc-systems` で URL を確認する
- URL が `githubConfigUrl` と一致しているか検証する

## 関連

- Issue #601: https://github.com/flipslidersand/dev-nodee-infrastructure/issues/601
