import json
from typing import Generator

import pytest
from _pytest.monkeypatch import MonkeyPatch
from airflow.models import Connection
from testcontainers.localstack import LocalStackContainer


@pytest.fixture(scope="session")
def localstack() -> Generator[LocalStackContainer, None, None]:
    """Set up a LocalStack container."""
    with LocalStackContainer() as localstack:
        yield localstack


@pytest.fixture(scope="session")
def monkeypatch_session() -> Generator[MonkeyPatch, None, None]:
    """Session-scoped monkeypatch fixture."""
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session", autouse=True)
def connection(monkeypatch_session, localstack, conn_id: str = "aws_default") -> None:
    """Session-scoped default AWS connection fixture pointing to LocalStack that is automatically used during tests."""
    c = Connection(
        conn_id=conn_id,
        conn_type="aws",
        extra=json.dumps({
            "aws_access_key_id": "foo",
            "aws_secret_access_key": "bar",
            "endpoint_url": localstack.get_url()
        })
    )
    monkeypatch_session.setenv(f"AIRFLOW_CONN_{conn_id.upper()}", c.get_uri())
