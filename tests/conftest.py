"""Gemeinsame Pytest-Fixtures für die Playwright-Tests der Arabisch-App."""
import pathlib
import socket
import subprocess
import sys
import time
import urllib.request

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
APP_DIR = REPO_ROOT / "arabisch-app"
SERVE_SCRIPT = pathlib.Path(__file__).resolve().parent / "serve.py"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def served_app():
    """Startet einen lokalen Server für arabisch-app/ und liefert die URL
    zu madina-arabisch.html. Läuft für die gesamte Testsession, wird beim
    Teardown beendet."""
    port = _free_port()
    proc = subprocess.Popen(
        [sys.executable, str(SERVE_SCRIPT), str(port), str(APP_DIR)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}/madina-arabisch.html"

    deadline = time.time() + 10
    started = False
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("Testserver (serve.py) ist vorzeitig beendet.")
        try:
            urllib.request.urlopen(url, timeout=0.5)
            started = True
            break
        except Exception:
            time.sleep(0.1)
    if not started:
        proc.terminate()
        proc.wait(timeout=5)
        raise RuntimeError("Testserver ist nicht rechtzeitig gestartet.")

    yield url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
