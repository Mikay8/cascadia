import os
import subprocess
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parent.parent

PROBE = "import config.settings.production as s; print(s.SECURE_SSL_REDIRECT)"

REQUIRED = {
    "DJANGO_SECRET_KEY": "test-secret",
    "DATABASE_URL": "postgres://u:p@localhost:5432/db",
    "DJANGO_ALLOWED_HOSTS": "example.test",
}


def load_production_settings(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    """Import production settings in a fresh interpreter so this test's settings stay intact."""
    clean = {k: v for k, v in os.environ.items() if not k.startswith(("DJANGO_", "DATABASE_"))}
    return subprocess.run(  # noqa: S603
        [sys.executable, "-c", PROBE],
        cwd=BACKEND,
        env={**clean, **env},
        capture_output=True,
        text=True,
        check=False,
    )


def test_production_settings_load_with_every_secret() -> None:
    result = load_production_settings(REQUIRED)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "True"


@pytest.mark.parametrize("missing", sorted(REQUIRED))
def test_production_settings_refuse_to_start_without(missing: str) -> None:
    env = {k: v for k, v in REQUIRED.items() if k != missing}

    result = load_production_settings(env)

    assert result.returncode != 0
    assert missing in result.stderr
