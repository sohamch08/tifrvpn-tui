"""Importing library and GUI modules must be safe without runtime dependencies."""

import subprocess
import sys
import unittest
from pathlib import Path


class ImportTests(unittest.TestCase):
    def test_all_modules_import_with_no_optional_dependencies_or_external_actions(self):
        import tifrvpn

        package_root = str(Path(tifrvpn.__file__).resolve().parent.parent)
        script = """
import sys
sys.path.insert(0, sys.argv[1])
import importlib.abc
import pathlib
import pkgutil
import socket
import subprocess
from unittest.mock import patch
class BlockOptional(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in {"gi", "PySide6", "numpy", "zxingcpp", "cryptography"}:
            raise AssertionError("Optional dependency loaded: " + fullname)
sys.meta_path.insert(0, BlockOptional())
def forbidden(*args, **kwargs):
    raise AssertionError("External operation during import")
with patch.object(subprocess, "run", forbidden), patch.object(subprocess, "Popen", forbidden), \\
        patch.object(socket, "create_connection", forbidden), patch.object(pathlib.Path, "read_text", forbidden):
    import tifrvpn
    for module in pkgutil.walk_packages(tifrvpn.__path__, "tifrvpn."):
        __import__(module.name)
    assert callable(tifrvpn.connect)
    assert callable(tifrvpn.disconnect)
"""
        result = subprocess.run(
            [sys.executable, "-I", "-S", "-c", script, package_root],
            check=False,
            cwd="/",
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
