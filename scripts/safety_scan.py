from __future__ import annotations

import argparse
from pathlib import Path


BLOCKED_EXTENSIONS = {
    ".pt",
    ".pth",
    ".ckpt",
    ".onnx",
    ".engine",
    ".tif",
    ".tiff",
    ".dm3",
    ".dm4",
    ".emd",
    ".emi",
    ".tar",
    ".gz",
    ".zip",
}

BLOCKED_TEXT = [
    "\\".join(["D:", "projects", "Gan_v3"]),
    "/".join(["D:", "projects", "Gan_v3"]),
    "\\".join(["D:", "projects", "Train dataset"]),
    "/".join(["D:", "projects", "Train dataset"]),
    "-".join(["quick", "label", "assist"]),
    "Hell" + "bender",
    "/" + "cluster" + "/",
    "gx" + "zmd",
    "project" + "_memory",
    "." + "hellbender" + "-project-memory",
]

SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", "*.egg-info"}
TEXT_EXTENSIONS = {".py", ".md", ".toml", ".yml", ".yaml", ".csv", ".json", ".cff", ".gitignore", ".gitattributes"}


def _is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {".gitignore", ".gitattributes"}


def scan_path(root: Path, max_file_mb: float = 5.0) -> list[str]:
    root = Path(root)
    failures: list[str] = []
    max_bytes = int(max_file_mb * 1024 * 1024)
    for path in root.rglob("*"):
        rel_parts = set(path.relative_to(root).parts)
        if rel_parts & SKIP_DIRS:
            continue
        if path.is_dir():
            continue
        rel = path.relative_to(root).as_posix()
        suffix = path.suffix.lower()
        if suffix in BLOCKED_EXTENSIONS:
            failures.append(f"blocked extension: {rel}")
        if path.stat().st_size > max_bytes:
            failures.append(f"file too large: {rel}")
        if _is_text_file(path):
            text = path.read_text(encoding="utf-8", errors="ignore")
            for pattern in BLOCKED_TEXT:
                if pattern in text:
                    failures.append(f"blocked text pattern {pattern!r}: {rel}")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Scan the public demo repository for unsafe files and private paths.")
    parser.add_argument("root", type=Path, nargs="?", default=Path("."))
    args = parser.parse_args()
    failures = scan_path(args.root)
    if failures:
        for failure in failures:
            print(failure)
        raise SystemExit(1)
    print("Safety scan passed")


if __name__ == "__main__":
    main()
