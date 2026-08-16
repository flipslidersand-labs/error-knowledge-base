---
title: "err.message をレスポンスに直接渡すパターンの漏洩"
tags: [javascript]
severity: medium
source: personal
---

# err.message をレスポンスに直接渡すパターンの漏洩

**発生プロジェクト**: `yukilabs-core/api-server`  
**関連 Issue**: #605 (fix) / #606 (prevention)  
**発見日**: 2026-08-02

---

## 事象

`/api/health/detailed` の 503 パスで `err.message` がそのままクライアントに返されていた。

```js
// 修正前
res.status(503).json({ status: "unhealthy", error: err.message });
```

---

## 見落とし原因（#414 セキュリティ監査で検出できなかった理由）

1. **監査スコープが不完全**: `src/index.js` のみを確認し `src/routes/` 配下を網羅していなかった
2. **テスト不足**: 503 パスのテストは status code のみ検証していた（`error` フィールドの中身を検証していなかった）
3. **catch ブロックのパターン盲点**: 正常系コードレビュー中心で、catch ブロック内のレスポンスに注意が向きにくい

---

## 修正内容

`monitoring.js` の 503/500 エラーパスで静的メッセージに変更。  
`authController.js` は `err.code` がある場合（意図的な構造化エラー）のみ `err.message` を使用。

```js
// 修正後パターン
res.status(503).json({ error: "Database connection failed" });

// authController パターン
const message = err.code ? err.message : "Authentication failed";
```

---

## 再発防止チェックリスト

セキュリティ監査・コードレビュー時に `catch` ブロック内を必ず確認する:

- [ ] `res.*.json(...)` に `err.message` / `err.stack` / `error.message` を直接渡していないか
- [ ] 500/503 レスポンスに動的な内部エラー情報が含まれていないか
- [ ] `err.code` がない外部ライブラリエラーが素通りしないか（DB, HTTP client, JWT lib など）

---

## CI での自動検出

```bash
# catch ブロック内の err.message 漏洩パターンを grep
grep -rn 'error: err\.message\|err\.message.*res\.' src/ \
  --include='*.js' --include='*.ts'
```

CI に組み込む場合は以下を `package.json` の `lint:security` スクリプトに追加:

```json
{
  "scripts": {
    "lint:security": "grep -rn 'error: err\\.message' src/ --include='*.js' && exit 1 || exit 0"
  }
}
```

---

## 教訓

- **catch ブロックは正常系と同じ厳密さでレビューする**
- テストは status code だけでなく **エラーレスポンスの `error` フィールドの中身を検証** する
- 外部ライブラリの例外は必ず `err.code` の有無でハンドリングを分岐する
