---
title: "master から分岐したブランチへの機能ポート手順"
tags: [go]
severity: medium
source: personal
---

# master から分岐したブランチへの機能ポート手順

## 状況

`perf/round11-optimizations` は master の round12/13 より前に分岐していた。
master で追加された TLS フィンガープリント基盤（#160 系）が存在しないため、
round11 ブランチで code-review した #207 等を実装するには先に基盤をポートする必要があった。

## 手順

1. master の該当ファイルを参照ソースとして使用（`flipslidersand/mesh-drop/` サブディレクトリ）
2. ポートしたい関数・型を特定して新ファイルに実装
3. 依存関係（import 追加）を忘れずに追加
4. コンパイルエラーから依存を芋づる式に発見する

## merge 時のコンフリクト解消方針

- セキュリティ修正・品質改善は HEAD（自分の実装）を保持
- master が HEAD より進化させたテストファイルは `git checkout --theirs` で採用
- 両方に存在する機能（`clear` vs `zeroBytes` 等）は master の関数名に統一
- master にしかない新関数（`BenchmarkDeriveChunkStreamKey` 等）は手動でマージ

## 注意

- `git checkout --ours` / `--theirs` 後は必ず `go build` + `go test` で確認
- noise.go の `clear(pt)` → `zeroBytes` 変更時は `zeroBytes` 関数の存在確認
- 同一ファイルに重複定義が生まれる場合（parseFingerprint 等）は `--ours` で回避し重複チェック
