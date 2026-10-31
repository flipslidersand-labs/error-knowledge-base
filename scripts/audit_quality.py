#!/usr/bin/env python3
"""errors/ の品質を決定的に測る(#129 第1段)。LLM は使わない。

欠落: 必須項目(原因/対処/予防)の見出しが無い、または見出しの下が空
断片: 本文が短すぎる、見出しが1つも無い

Usage: python3 scripts/audit_quality.py [--json] [--list]
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import parse_frontmatter  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MIN_BODY_CHARS = 200
REQUIRED_META = ("title", "tags", "severity", "source")

# 見出し語の揺れを吸収する(実エントリの見出しから採取)
SECTIONS = {
    "cause": ("原因", "根本原因", "発生条件", "仕様", "なぜ", "背景", "why", "cause"),
    # 「対策」は修正と予防のどちらの意味でも使われているため両方に入れる
    "fix": (
        "解決",
        "対処",
        "対応",
        "対策",
        "手順",
        "修正",
        "回避",
        "fix",
        "solution",
        "workaround",
    ),
    "prevention": ("予防", "再発防止", "防止", "教訓", "対策", "prevention", "lesson"),
}
HEADING = re.compile(r"^(#{1,4})\s*(.+?)\s*$", re.M)
CODE_MARK = "[code-block]"  # コードだけの節を「空」と誤判定しないための十分な長さの目印


def split_sections(body: str) -> list[tuple[str, str]]:
    """(見出し, 配下の本文) のリスト。同階層以上の次の見出しまでを配下とする(小見出しを含む)。

    コードフェンス内の # は見出しとして扱わない。先頭の h1 が題名(直後がより深い見出し)なら除く。
    """
    clean = re.sub(r"```.*?```", CODE_MARK, body, flags=re.S)
    marks = [(len(m.group(1)), m) for m in HEADING.finditer(clean)]
    if len(marks) > 1 and marks[0][0] == 1 and marks[1][0] > 1:
        marks = marks[1:]
    out = []
    for i, (level, m) in enumerate(marks):
        end = next((n.start() for lv, n in marks[i + 1 :] if lv <= level), len(clean))
        out.append((m.group(2), clean[m.end() : end].strip(" \n-*|:")))
    return out


def audit_entry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    sections = split_sections(body)
    problems = []

    for key in REQUIRED_META:
        if not meta.get(key):
            problems.append(f"meta:{key}")
    if len(body.strip()) < MIN_BODY_CHARS:
        problems.append("fragment:short")
    if not sections:
        problems.append("fragment:no-headings")

    for name, words in SECTIONS.items():
        hits = [c for h, c in sections if any(w in h.lower() for w in words)]
        if not hits:
            problems.append(f"missing:{name}")
        elif not any(len(c) >= 10 for c in hits):
            problems.append(f"empty:{name}")
    shown = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
    return {"path": str(shown), "chars": len(body.strip()), "problems": problems}


def main() -> int:
    results = [audit_entry(p) for p in sorted((ROOT / "errors").rglob("*.md"))]
    n = len(results)
    counts: dict[str, int] = {}
    for r in results:
        for p in r["problems"]:
            counts[p] = counts.get(p, 0) + 1
    flagged = [r for r in results if r["problems"]]

    if "--json" in sys.argv:
        print(
            json.dumps(
                {"total": n, "flagged": len(flagged), "counts": counts, "entries": results},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    print(f"total={n} flagged={len(flagged)} ({len(flagged) / n:.0%})" if n else "total=0")
    for k, v in sorted(counts.items(), key=lambda kv: -kv[1]):
        print(f"  {k:22s} {v:3d} ({v / n:.0%})")
    if "--list" in sys.argv:
        for r in flagged:
            print(f"{r['path']}: {', '.join(r['problems'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
