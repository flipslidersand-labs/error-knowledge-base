# Changelog

All notable changes to this project are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
Versioning: [Semantic Versioning](https://semver.org/)

> No version has been tagged yet. The entries below summarize the git history up to the first release.

---

## [Unreleased]

### Added
- Error knowledge base in `errors/`, published as a static site on GitHub Pages.
- Tags, search and related-error links; a `source` field to separate first-hand experience from web references.
- Categories for ci, infra, runtime, rust and tooling, and imported knowledge entries (#1, #14, #15, #16).
- `scripts/audit_quality.py`: deterministic check for missing or fragmentary sections in `errors/`.
- Secret scan with gitleaks in CI (#29).

### Security
- Stored XSS fix: tags are escaped and rendered Markdown is sanitized (#21).

### Fixed
- Pages deployment 403 (`contents: write`) and the actions-gh-pages update to v4 (#17, #92).
- Quality audit no longer requires a "prevention" section (#159).
