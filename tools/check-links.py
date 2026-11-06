#!/usr/bin/env python3
"""Check this repository's routing. Run from the repository root:

    python3 tools/check-links.py

The same script is used in hkarn/WebDev-Studio and hkarn/tech-research; keep the copies identical.

Checks, for every tracked or untracked-but-not-ignored Markdown file:
1. Every relative Markdown link points at a file or folder that exists, and every #anchor
   matches a heading in the target file.
2. Every file is reachable from AGENTS.md by following links. A link to a folder reaches
   everything inside it (use that for packages: an eval folder, history/).
3. Nothing links into inbox/ except inbox/README.md.

Files that need no route: the root README.md and tool files (CLAUDE.md, GEMINI.md, .gitignore, .gitattributes,
.github/), everything in inbox/ and tools/. Imported material under history/<name>/ (any
subfolder of history/) keeps its original links, which may point at files that were not imported,
so links inside it are not checked; it is reached through a folder link. Exits 1 on any problem.
"""

import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

ROOT = Path.cwd()
ENTRY = "AGENTS.md"
UNROUTED_PREFIXES = ("inbox/", "tools/", ".github/", ".claude/")
UNROUTED_FILES = {"README.md", "CLAUDE.md", "GEMINI.md", ".gitignore", ".gitattributes", ".editorconfig"}

LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|!\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")


def repo_files():
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, check=True, encoding="utf-8",
    ).stdout
    return sorted({line for line in out.splitlines() if line and (ROOT / line).is_file()})


def slug(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower().replace("`", "")
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path, cache={}):
    if path not in cache:
        found, counts, in_fence = set(), {}, False
        for line in (ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines():
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            m = None if in_fence else HEADING.match(line)
            if m:
                s = slug(m.group(1))
                n = counts.get(s, 0)
                counts[s] = n + 1
                found.add(s if n == 0 else f"{s}-{n}")
        cache[path] = found
    return cache[path]


def links(path):
    in_fence = False
    for no, line in enumerate((ROOT / path).read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        line = re.sub(r"`[^`]*`", "", line)
        for m in LINK.finditer(line):
            yield no, m.group(1) or m.group(2)


def main():
    files = repo_files()
    file_set = set(files)
    problems = []
    edges = {}

    for f in files:
        if not f.endswith(".md"):
            continue
        edges[f] = []
        if f.startswith("history/") and f.count("/") >= 2:
            continue
        base = PurePosixPath(f).parent
        for no, target in links(f):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("//"):
                continue
            target, _, anchor = target.partition("#")
            target = unquote(target)
            if not target:
                resolved = f
            else:
                resolved = str(PurePosixPath(*(base / target).parts)) if not target.startswith("/") else target.lstrip("/")
                parts = []
                for p in PurePosixPath(resolved).parts:
                    if p == "..":
                        if parts:
                            parts.pop()
                    elif p != ".":
                        parts.append(p)
                resolved = "/".join(parts)
            where = f"{f}:{no}"
            if resolved.startswith("inbox/") and resolved != "inbox/README.md" and not f.startswith("inbox/"):
                problems.append(f"{where}: links into inbox/ ({target})")
            if resolved in file_set:
                edges[f].append(resolved)
                if anchor and resolved.endswith(".md") and anchor.lower() not in anchors(resolved):
                    problems.append(f"{where}: no heading for #{anchor} in {resolved}")
            elif resolved and (ROOT / resolved).is_dir():
                prefix = resolved.rstrip("/") + "/"
                if resolved in ("", "."):
                    problems.append(f"{where}: links to the repository root")
                    continue
                edges[f].extend(x for x in files if x.startswith(prefix))
            else:
                problems.append(f"{where}: broken link {target}")

    if ENTRY not in file_set:
        problems.append(f"{ENTRY} is missing")
    seen, todo = set(), [ENTRY]
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        todo.extend(edges.get(f, []))
    for f in files:
        if f in seen or f in UNROUTED_FILES or f.startswith(UNROUTED_PREFIXES):
            continue
        problems.append(f"{f}: not reachable from {ENTRY}; add it to its folder's router")

    for p in problems:
        print(p)
    print(f"{len(files)} files, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
