"""Regression test: importing the Aden client module must not eagerly load
httpx.

httpx is a real dependency of this module, but only needed once an actual
Aden API call is made (AdenCredentialClient._get_client /
_request_with_retry) — not merely to import `framework`. httpx also has an
optional CLI extra (rich + pygments + markdown-it-py) that this repo pulls
in transitively via fastmcp, so an eager `import httpx` here loads that
whole syntax-highlighting stack too on every `import framework`, unrelated
to whether Aden credentials are ever used. See #7323.

Run in a subprocess (not in-process) because other tests in the same pytest
session may import httpx via unrelated paths, which would make an in-process
``'httpx' not in sys.modules`` assertion order-dependent and flaky.
"""

import subprocess
import sys
from pathlib import Path

_CORE_DIR = Path(__file__).resolve().parents[4]


def test_importing_client_module_does_not_load_httpx():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import framework.credentials.aden.client; import sys; print('httpx' in sys.modules)",
        ],
        cwd=_CORE_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False", f"httpx was eagerly imported:\n{result.stderr}"


def test_get_client_lazily_loads_httpx_and_returns_working_client():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys\n"
                "from framework.credentials.aden.client import AdenCredentialClient, AdenClientConfig\n"
                "assert 'httpx' not in sys.modules\n"
                "client = AdenCredentialClient(AdenClientConfig(base_url='https://example.invalid', api_key='x'))\n"
                "c = client._get_client()\n"
                "assert 'httpx' in sys.modules\n"
                "import httpx\n"
                "assert isinstance(c, httpx.Client)\n"
                "client.close()\n"
                "print('ok')\n"
            ),
        ],
        cwd=_CORE_DIR,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"
