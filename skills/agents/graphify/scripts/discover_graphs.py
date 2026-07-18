#!/usr/bin/env python3
"""List relevant Graphify graphs without reading their graph payloads."""

from __future__ import annotations

import argparse
import os
import subprocess
from datetime import datetime
from pathlib import Path


PRUNE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".worktrees",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
}
TEST_DIRS = {"test", "tests", "__tests__", "spec", "specs"}


def repository_root(path: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()
    return path


def is_test_surface(surface: Path, scan_root: Path) -> bool:
    try:
        parts = surface.relative_to(scan_root).parts
    except ValueError:
        parts = surface.parts
    return any(part.lower() in TEST_DIRS for part in parts)


def relation(surface: Path, target: Path) -> tuple[int, int, str]:
    try:
        relative = target.relative_to(surface)
        return 0, len(relative.parts), "covers-target"
    except ValueError:
        pass
    try:
        relative = surface.relative_to(target)
        return 1, len(relative.parts), "inside-target"
    except ValueError:
        return 2, len(surface.parts), "same-repository"


def discover(scan_root: Path) -> list[Path]:
    graphs: list[Path] = []
    for current, directories, _files in os.walk(scan_root):
        current_path = Path(current)
        directories[:] = sorted(name for name in directories if name not in PRUNE_DIRS)
        if current_path.name == "graphify-out":
            graph = current_path / "graph.json"
            if graph.is_file():
                graphs.append(graph.resolve())
            directories[:] = []
    return graphs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Discover concise Graphify graph candidates for a task scope."
    )
    parser.add_argument("--root", default=".", help="Task path or directory (default: current directory)")
    parser.add_argument("--include-tests", action="store_true", help="Include test-only graph surfaces")
    parser.add_argument("--max-results", type=int, default=12, help="Maximum candidates to print (default: 12)")
    args = parser.parse_args()

    target = Path(args.root).expanduser().resolve()
    if target.is_file():
        target = target.parent
    if not target.exists():
        parser.error(f"root does not exist: {target}")
    if args.max_results < 1:
        parser.error("--max-results must be positive")

    scan_root = repository_root(target)
    graphs = discover(scan_root)
    candidates = []
    for graph in graphs:
        surface = graph.parent.parent
        test_surface = is_test_surface(surface, scan_root)
        if test_surface and not args.include_tests and not is_test_surface(target, scan_root):
            continue
        rank, distance, scope = relation(surface, target)
        candidates.append((rank, distance, test_surface, str(surface), scope, surface, graph))

    candidates.sort()
    print(f"scan_root={scan_root}")
    print(f"graphs={len(candidates)}")
    for index, (_rank, _distance, _test, _name, scope, surface, graph) in enumerate(
        candidates[: args.max_results], start=1
    ):
        stat = graph.stat()
        size_mib = stat.st_size / (1024 * 1024)
        modified = datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds")
        print(
            f"{index}. scope={scope} surface={surface} graph={graph} "
            f"size_mib={size_mib:.1f} modified={modified}"
        )
    remaining = len(candidates) - args.max_results
    if remaining > 0:
        print(f"omitted={remaining}; rerun with --max-results {len(candidates)} if needed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
