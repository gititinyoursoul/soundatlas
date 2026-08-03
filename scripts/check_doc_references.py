"""Check active documentation for missing repository-relative path references."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PATH_PATTERN = re.compile(
    r"(?<![\w./-])(?:AGENTS\.md|README\.md|(?:\.codex|backend|data|docs|frontend|prompts|scripts)/[^\s`<>\])}\"']+)"
)
TRAILING_PUNCTUATION = ".,;:!?)]}\"'"


def active_markdown_files(root: Path) -> list[Path]:
    files = [root / "AGENTS.md", root / "README.md"]
    files.extend(path for path in (root / "docs").rglob("*.md"))
    files.extend(path for path in (root / "prompts").rglob("*.md"))
    files.extend(path for path in (root / ".codex" / "skills").rglob("*.md"))
    return sorted(
        path
        for path in set(files)
        if path.is_file()
        and path.relative_to(root) != Path("docs/done.md")
        and Path("docs/content/routes") not in path.relative_to(root).parents
    )


def candidate_paths(line: str) -> list[str]:
    candidates = []
    for match in PATH_PATTERN.finditer(line):
        candidate = match.group(0).rstrip(TRAILING_PUNCTUATION)
        if any(marker in candidate for marker in ("*", "<", ">", "&lt;", "&gt;")):
            continue
        if "YYYY-MM-DD" in candidate or "/backend/frontend" in candidate:
            continue
        if candidate.startswith("data/enrichment/schemas/"):
            continue
        if "." not in Path(candidate).name:
            continue
        candidates.append(candidate)
    return candidates


def find_missing_references(root: Path) -> list[tuple[Path, int, str]]:
    missing = []
    for source in active_markdown_files(root):
        for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            for candidate in candidate_paths(line):
                targets = [root / candidate]
                if candidate.startswith("scripts/"):
                    targets.append(root / "backend" / candidate)
                if not any(target.exists() for target in targets):
                    missing.append((source.relative_to(root), line_number, candidate))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    missing = find_missing_references(root)
    if missing:
        for source, line_number, candidate in missing:
            print(f"{source}:{line_number}: missing repository path: {candidate}")
        return 1
    print("Documentation references are valid on active guidance surfaces.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
