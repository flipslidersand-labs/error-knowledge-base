---
title: "Claude Code 無応答 — UserPromptSubmit フック参照切れ"
tags: [tooling]
severity: medium
source: personal
---

# Claude Code 無応答 — UserPromptSubmit フック参照切れ

## 症状

新規セッションで入力しても読み込み後にサイレント（応答返らない）。

## 原因

`UserPromptSubmit` フックが2箇所に登録されており、片方のスクリプトパスが古いままだった。

| 設定ファイル                                           | スクリプト                  | 状態                      |
| ------------------------------------------------------ | --------------------------- | ------------------------- |
| `~/.claude/projects/.../settings.json`（プロジェクト） | `qdrant-rag-hook.py`        | 正常                      |
| `~/.claude/settings.json`（ユーザー）                  | `rag-hook.py`（存在しない） | 毎回エラー → タイムアウト |

`rag-hook.py` はリファクタで `qdrant-rag-hook.py` にリネームされたが、ユーザー設定側の参照が更新されていなかった。

## 修正

```bash
# どのファイルが古い名前を参照しているか確認
grep -r "rag-hook.py" ~/.claude/

# ユーザー設定の壊れた UserPromptSubmit エントリを削除
# ~/.claude/settings.json の hooks.UserPromptSubmit から該当エントリを除去
```

## 確認方法

```bash
cat ~/.claude/settings.json | python3 -c "
import sys,json; d=json.load(sys.stdin)
print(d.get('hooks',{}).get('UserPromptSubmit',[]))
"
```

→ 存在しないパスを参照しているエントリがないこと

## 教訓

- フック用スクリプトをリネームしたら `~/.claude/settings.json` と `.claude/settings.json` の両方を更新する
- 無応答・遅延の第一チェックポイントは `UserPromptSubmit` フックのスクリプトパス
