"""Test-collection guards for red_python.

red_python is a Windows desktop application: some test modules import
Windows-only stdlib modules (`winreg`) and cannot even be collected on the
Linux governance host where the Cerberus pre-push gate runs the suite.
Skipping them off-platform keeps the gate meaningful (the cross-platform
tests still run) without pretending the Windows behavior was verified here.
"""

import sys

collect_ignore = []
if sys.platform != "win32":
    collect_ignore.append("test_shell_and_app.py")
