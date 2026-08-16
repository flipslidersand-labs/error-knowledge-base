---
title: "ARC controller で GitHub PAT 認証エラー 401 Bad credentials"
tags: [github, arc, authentication, kubernetes]
severity: high
source: personal
date: "2026-08-14"
---

## 症状

DS1 WSL2 上の summerwind ARC controller が runner pod を起動しようとした際、GitHub API 呼び出しで以下のエラー:

```
Failed to get new registration token
error: "failed to create registration token:
  POST https://api.github.com/repos/flipslidersand/safecode-arena/actions/runners/registration-token:
  401 Bad credentials []"
```

RunnerDeployment は created だが、pod は未起動。ログで繰り返し認証エラーが出ている。

## 原因

GitHub PAT が無効:

1. YUKI k3s から base64 デコード → DS1 secret として設定
2. ARC controller が secret から github_token を読み込んで API 呼び出し
3. トークンが無効（期限切れ/権限不足/破損）→ 401

デコード時の問題の可能性:

- Base64 二重化
- ホスト間でのエンコード差異
- Token 内の特殊文字処理

## 解決策

**1. 新規 GitHub PAT を生成**

```bash
# GitHub Settings → Personal access tokens → Tokens (classic)
# Scope 選択:
#   - repo (full control)
#   - admin:org_hook (for runner registration)
# トークン保存: ~/.config/github-token
```

**2. Secret を更新**

```bash
export GITHUB_TOKEN=$(cat ~/.config/github-token)
ssh ds1 'wsl -u root bash' << 'EOF'
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
# 古い secret 削除
kubectl delete secret -n arc-runners arc-github-secret 2>/dev/null || true
# 新規 secret 作成
kubectl create secret generic arc-github-secret \
  -n arc-runners \
  --from-literal=github_token="$GITHUB_TOKEN"
EOF
```

**3. ARC pod を再起動して secret 再読み込み**

```bash
kubectl delete pod -n arc-systems -l app.kubernetes.io/name=actions-runner-controller
# Pod 自動再起動（deployment が管理）
```

**4. Runner pod 起動を確認**

```bash
kubectl get pods -n arc-runners
# 1-3 分で ci-pool-xxxxx-yyyyy pod が作成される
```

## 予防

1. **PAT の直接生成**: 別ホストから複製しない
2. **Scope 確認**: `repo` + `admin:org_hook` が必須
3. **Secret 内容検証**:
   ```bash
   kubectl get secret -n arc-runners arc-github-secret -o jsonpath='{.data.github_token}' | base64 -d | head -c 20
   # ghp_xxxx... のような形式で始まること確認
   ```
4. **ログ監視**: `kubectl logs -f -n arc-systems -l app.kubernetes.io/name=actions-runner-controller`

## 関連

- [[project_ds1_k3s_deployment_840]] — DS1 k3s デプロイで遭遇
- [[errors/system/github-app-org-level-runners-404.md]] — 別の GitHub auth エラー
