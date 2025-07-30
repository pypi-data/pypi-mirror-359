import pytest

from tosspayments_server_sdk.client import Client


class TestClient:

    def test_client_initialization_with_valid_secret_key(self, test_secret_key):
        client = Client(secret_key=test_secret_key)

        assert client.config.secret_key == test_secret_key
        assert client.is_test_mode is True
        assert client.is_live_mode is False
        assert hasattr(client, "payments")

    def test_client_initialization_with_invalid_secret_key(self):
        with pytest.raises(ValueError, match="secret_key must start with"):
            Client(secret_key="invalid_secret_key")

    def test_live_mode_detection(self, live_secret_key):
        client = Client(secret_key=live_secret_key)

        assert client.is_live_mode is True
        assert client.is_test_mode is False

    def test_custom_configuration(self, test_secret_key):
        client = Client(secret_key=test_secret_key, timeout=60, max_retries=5)

        assert client.config.timeout == 60
        assert client.config.max_retries == 5
