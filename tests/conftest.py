"""Test-collection guards for red_python.

red_python is a Windows desktop application: some test modules import
Windows-only stdlib modules (`winreg`) and cannot even be collected on the
Linux host where the suite is normally run. Skipping them off-platform keeps
the run meaningful (the cross-platform tests still execute) without pretending
the Windows behavior was verified here.
"""

import sys

collect_ignore = []
if sys.platform != "win32":
    collect_ignore.append("test_shell_and_app.py")
