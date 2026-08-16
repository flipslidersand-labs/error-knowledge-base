---
title: "ARC listener crash loop — org-level 404 / scale set ID 不一致"
tags: [ci]
severity: medium
source: personal
---

# ARC listener crash loop — org-level 404 / scale set ID 不一致

## エラーメッセージ

```
failed to create message session: failed to do the session request:
request POST https://broker.actions.githubusercontent.com/rest/_apis/runtime/runnerscalesets/1/sessions
failed(status="404 Not Found"): No runner scale set found with identifier 1.
```

または:

```
POST https://api.github.com/orgs/<org>/actions/runners/registration-token 404 Not Found
```

## 症状

- `kubectl get pods -n arc-systems` で listener が `Error` / `CrashLoopBackOff`
- `classify`（Risk Classify 等）が QUEUED のまま2時間以上詰まる
- コントローラー pod は Running だが reconcile loop が止まらない

## 原因

| パターン         | 原因                                                                                                                |
| ---------------- | ------------------------------------------------------------------------------------------------------------------- |
| org-level 404    | GitHub org が未作成、または org-level runner 権限なし。`githubConfigUrl` が `https://github.com/<org>` になっている |
| scale set ID 404 | 旧 listener が過去の scale set ID（例: 1）でセッション取得を試みるが、GitHub 側で削除済み                           |

## 解決手順

### org-level 404 の場合（#411 の症状）

`values.yaml` または Helm chart の `githubConfigUrl` を repo-level に変更：

```yaml
# 変更前（org-level）
githubConfigUrl: https://github.com/<org>

# 変更後（repo-level）
githubConfigUrl: https://github.com/<owner>/<repo>
```

その後 `helm upgrade` または `kubectl rollout restart` で listener を再起動。

### scale set ID 404 の場合

旧 ID を参照している listener pod を削除すると、コントローラーが正しい ID で新 pod を起動する：

```bash
kubectl delete pod -n arc-systems <old-listener-pod>
```

1つでも Running な listener があれば、Error pod の削除後に自己回復する（正常挙動）。

## 回帰確認コマンド

```bash
# pod 状態
kubectl get pods -n arc-systems

# listener ログ（正常: "Getting next message" が繰り返す）
kubectl logs -n arc-systems <listener-pod> --tail=10

# QUEUED 詰まりなし確認
gh run list --repo <owner>/<repo> --limit 20 --json status | jq '[.[] | select(.status=="queued")] | length'
```

## org-level へ戻す手順（#689 GitHub org 作成後）

1. GitHub org を作成し、ランナー権限を付与
2. `githubConfigUrl` を `https://github.com/<new-org>` に変更
3. `helm upgrade` で反映
4. listener が 404 なく起動することを確認

関連: #411（repo-level 修正）/ #689（org 作成）/ #750（回帰検証）
