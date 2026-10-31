#!/usr/bin/env python3
"""audit_quality.py の判定ロジックに対する回帰テスト（pytest 非依存）。

python tests/test_audit_quality.py
"""

import importlib.util
import tempfile
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "kbaudit", Path(__file__).resolve().parent.parent / "scripts" / "audit_quality.py"
)
a = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a)

META = '---\ntitle: "t"\ntags: [x]\nseverity: high\nsource: personal\n---\n'
PAD = "詳細な説明文。" * 20


def audit(body: str) -> list[str]:
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "e.md"
        p.write_text(META + body, encoding="utf-8")
        return a.audit_entry(p)["problems"]


def test_complete_entry_has_no_problems():
    body = f"## 症状\n{PAD}\n## 原因\n{PAD}\n## 解決策\n{PAD}\n## 予防\n{PAD}\n"
    assert audit(body) == []


def test_missing_prevention_detected():
    body = f"## 症状\n{PAD}\n## 原因\n{PAD}\n## 解決策\n{PAD}\n"
    assert audit(body) == ["missing:prevention"]


def test_fix_under_subheadings_is_not_empty():
    body = f"## 症状\n{PAD}\n## 原因\n{PAD}\n## 解決策\n### 即時対策\n{PAD}\n## 予防\n{PAD}\n"
    assert audit(body) == []


def test_fix_with_code_only_is_not_empty():
    body = f"## 症状\n{PAD}\n## 原因\n{PAD}\n## 解決策\n```bash\nls\n```\n## 予防\n{PAD}\n"
    assert audit(body) == []


def test_h1_sections_and_h1_title():
    body = f"# 題名\n## 症状\n{PAD}\n## 原因\n{PAD}\n## 解決策\n{PAD}\n## 予防\n{PAD}\n"
    assert audit(body) == []
    body = f"# 症状\n{PAD}\n# 原因\n{PAD}\n# 解決策\n{PAD}\n# 予防\n{PAD}\n"
    assert audit(body) == []


def test_cause_synonyms_condition_and_spec():
    for head in ("発生条件", "正しい仕様"):
        body = f"## 症状\n{PAD}\n## {head}\n{PAD}\n## 解決策\n{PAD}\n## 予防\n{PAD}\n"
        assert audit(body) == []


def test_hash_inside_code_fence_is_not_heading():
    body = f"## 症状\n```\n# 予防\n```\n{PAD}\n## 原因\n{PAD}\n## 解決策\n{PAD}\n"
    assert audit(body) == ["missing:prevention"]


def test_fragment_without_headings():
    probs = audit("短い断片")
    assert "fragment:short" in probs and "fragment:no-headings" in probs


def test_missing_meta():
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "e.md"
        p.write_text('---\ntitle: "t"\n---\n' + PAD, encoding="utf-8")
        assert "meta:severity" in a.audit_entry(p)["problems"]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok {name}")
