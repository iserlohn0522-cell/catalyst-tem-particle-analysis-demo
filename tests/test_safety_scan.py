from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_safety_scan():
    root = Path(__file__).resolve().parents[1]
    module_path = root / "scripts" / "safety_scan.py"
    spec = importlib.util.spec_from_file_location("safety_scan", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_safety_scan_allows_synthetic_public_files(tmp_path: Path) -> None:
    scanner = _load_safety_scan()
    (tmp_path / "README.md").write_text("Synthetic public demo only\n", encoding="utf-8")
    (tmp_path / "examples").mkdir()
    (tmp_path / "examples" / "synthetic.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    assert scanner.scan_path(tmp_path) == []


def test_safety_scan_blocks_weights_and_private_paths(tmp_path: Path) -> None:
    scanner = _load_safety_scan()
    (tmp_path / "model.pt").write_bytes(b"not a real model")
    private_path = "/".join(["D:", "projects", "Gan_v3"])
    (tmp_path / "notes.md").write_text(f"{private_path} should not appear\n", encoding="utf-8")

    failures = scanner.scan_path(tmp_path)

    assert any("blocked extension" in failure for failure in failures)
    assert any("blocked text pattern" in failure for failure in failures)
