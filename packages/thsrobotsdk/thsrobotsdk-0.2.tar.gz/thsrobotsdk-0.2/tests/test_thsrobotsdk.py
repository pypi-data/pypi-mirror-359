import pytest

from thsrobotsdk import ThsrobotSDK, RequestError


@pytest.fixture
def mock_sdk() -> ThsrobotSDK:
    return ThsrobotSDK(
        server_ip="127.0.0.1",
        secret_id="mock_secret_id",
        secret_key="mock_secret_key"
    )


def test_get_assets(sdk: ThsrobotSDK):
    with pytest.raises(RequestError):
        sdk.get_order()


def test_get_position(sdk: ThsrobotSDK):
    with pytest.raises(RequestError):
        sdk.get_position()


def test_get_order(sdk: ThsrobotSDK):
    with pytest.raises(RequestError):
        sdk.get_order()
