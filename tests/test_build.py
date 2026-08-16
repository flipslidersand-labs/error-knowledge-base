#!/usr/bin/env python3
"""build.py の frontmatter 正規化に対する回帰テスト（pytest 非依存）。

    python tests/test_build.py
"""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "kbbuild", Path(__file__).resolve().parent.parent / "scripts" / "build.py"
)
b = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(b)


def test_tags_with_inner_comma():
    meta, _ = b.parse_frontmatter('---\ntitle: "t"\ntags: ["a, b", c]\nseverity: high\n---\nbody\n')
    assert meta["tags"] == ["a, b", "c"]


def test_severity_fallback():
    assert b.normalize_severity("critical") == "medium"
    assert b.normalize_severity("High") == "high"
    assert b.normalize_severity(None) == "medium"


def test_normalize_tags_variants():
    assert b.normalize_tags("go") == ["go"]
    assert b.normalize_tags(["a", " b ", ""]) == ["a", "b"]
    assert b.normalize_tags(None) == []


def test_invalid_yaml_falls_back():
    meta, body = b.parse_frontmatter('---\ntitle: "x\n  bad: [\n---\nBODY\n')
    assert isinstance(meta, dict)
    assert "BODY" in body


def test_no_frontmatter():
    meta, body = b.parse_frontmatter("# just h1\n\ntext")
    assert meta == {} and "text" in body


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in fns:
        fn()
        print(f"  ok {fn.__name__}")
    print(f"✅ {len(fns)} passed")
