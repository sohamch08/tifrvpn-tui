"""Module imports load dependencies without starting application operations."""

import subprocess
import sys
import unittest
from pathlib import Path

import tifrvpn


class ImportTests(unittest.TestCase):
    def test_all_modules_import_without_external_actions(self):
        package_root = str(Path(tifrvpn.__file__).resolve().parent.parent)
        script = """
import sys
sys.path.insert(0, sys.argv[1])
import pathlib
import pkgutil
import socket
import subprocess
from types import ModuleType
from unittest.mock import patch
def forbidden(*args, **kwargs):
    raise AssertionError("External operation during import")
# Supply dependency interfaces without running third-party initialization.
# Importing a name is allowed; calling it to start an operation is not.
for name in (
    "gi", "gi.repository", "cryptography", "cryptography.hazmat",
    "cryptography.hazmat.primitives", "cryptography.hazmat.primitives.serialization",
    "PySide6", "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets",
    "PySide6.QtMultimedia", "numpy", "zxingcpp",
):
    module = ModuleType(name)
    module.__path__ = []
    module.__getattr__ = lambda name: forbidden
    sys.modules[name] = module
sys.modules["gi"].require_version = lambda *args: None
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
