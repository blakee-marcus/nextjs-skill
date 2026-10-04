from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "verify_public_surface", ROOT / "scripts" / "verify_public_surface.py"
)
assert SPEC is not None
assert SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PublicSurfaceTests(unittest.TestCase):
    def test_repository_passes(self) -> None:
        self.assertEqual(MODULE.verify(ROOT), [])

    def test_machine_specific_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in MODULE.REQUIRED_FILES:
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("placeholder\n", encoding="utf-8")
            (root / "README.md").write_text(
                "See /Users/example/private/project for setup.\n", encoding="utf-8"
            )
            errors = MODULE.verify(root)
            self.assertTrue(
                any("machine-specific home path" in error for error in errors), errors
            )

    def test_missing_local_markdown_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            readme.write_text("[missing](references/missing.md)\n", encoding="utf-8")
            errors = MODULE.local_link_errors(root, readme, readme.read_text())
            self.assertEqual(errors, ["README.md: missing local link: references/missing.md"])


if __name__ == "__main__":
    unittest.main()
