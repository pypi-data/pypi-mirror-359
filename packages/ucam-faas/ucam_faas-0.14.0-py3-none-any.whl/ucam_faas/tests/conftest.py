from typing import Any

import pytest
from cloudevents.http.event import CloudEvent

from ucam_faas.testing import event_app_test_client_factory

__all__ = ("event_app_test_client_factory",)


@pytest.fixture()
def valid_cloud_event() -> Any:
    return CloudEvent(
        data={"foo": "bar"}, attributes={"source": "ucam_faas", "type": "ucam_faas_event"}
    )
