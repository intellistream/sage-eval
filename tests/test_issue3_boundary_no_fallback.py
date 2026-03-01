from __future__ import annotations

from pathlib import Path


def _package_root() -> Path:
    return Path(__file__).resolve().parents[1] / "src" / "sage_libs" / "sage_eval"


def test_metrics_do_not_use_importerror_fallbacks() -> None:
    metrics_files = [
        _package_root() / "metrics" / "accuracy.py",
        _package_root() / "metrics" / "bleu.py",
        _package_root() / "metrics" / "f1.py",
    ]
    for file_path in metrics_files:
        source = file_path.read_text(encoding="utf-8")
        assert "except ImportError" not in source
        assert "_HAS_SAGE" not in source


def test_register_module_has_no_optional_registration_branch() -> None:
    register_file = _package_root() / "_register.py"
    source = register_file.read_text(encoding="utf-8")
    assert "except ImportError" not in source
    assert "_SAGE_REGISTERED" not in source
