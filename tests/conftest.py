"""Test-collection guards for red_python.

red_python is a Windows desktop application: some test modules import
Windows-only stdlib modules (`winreg`) and cannot even be collected on the
Linux host where the suite is normally run. Skipping them off-platform keeps
the run meaningful (the cross-platform tests still execute) without pretending
the Windows behavior was verified here.
"""

import sys
import time

collect_ignore = []
if sys.platform != "win32":
    collect_ignore.append("test_shell_and_app.py")


# --max-seconds enforcement for the fast unit lane (GS2-210-zero-hardcoded-
# invariants / test_timer_guard axiom: the pre-commit unit lane must stay
# <= 2.0s so it can be run on every commit without friction).
#
# DEBT-SLOW-TEST-SUITE-TIERING's own `verification_command`
# (`pytest -m 'not slow' --max-seconds 2.0`) named a flag that did not exist
# anywhere in this repo or in any installed plugin -- a prior close of that
# ticket argued the flag was bogus and left it at that (reverted by the
# fraud audit in d9fc277 for closing without the finding actually
# resolving). The flag is implemented for real here instead of arguing the
# instrument away: pytest_addoption registers it, pytest_sessionfinish
# measures the actual wall-clock duration of the run and fails the session
# if it exceeds the ceiling, so the invariant the ticket describes is
# actually enforced, not just documented in prose.
def pytest_addoption(parser):
    parser.addoption(
        "--max-seconds",
        action="store",
        type=float,
        default=None,
        help="Fail the run if the total test session exceeds this many seconds.",
    )


def pytest_sessionstart(session):
    session._max_seconds_start = time.monotonic()


def pytest_sessionfinish(session, exitstatus):
    max_seconds = session.config.getoption("--max-seconds")
    if max_seconds is None:
        return
    elapsed = time.monotonic() - session._max_seconds_start
    if elapsed > max_seconds:
        print(
            f"\nFAILED: test session took {elapsed:.2f}s, "
            f"exceeding --max-seconds={max_seconds:.2f}s ceiling."
        )
        session.exitstatus = 1
