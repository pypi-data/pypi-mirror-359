from tosspayments_server_sdk.config import Config
from tosspayments_server_sdk.http_client import HTTPClient
from tosspayments_server_sdk.resources.payments import PaymentResource
from tosspayments_server_sdk.resources.webhooks import WebhookResource


class Client:

    def __init__(
        self,
        secret_key: str,
        api_version: str = "v1",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """Initialize TossPayments client.

        Args:
            secret_key: TossPayments secret key (토스페이먼츠 시크릿 키)
            api_version: API version (API 버전)
            timeout: Request timeout in seconds (요청 타임아웃 초)
            max_retries: Maximum retry count (최대 재시도 횟수)
        """
        self.config = Config(
            secret_key=secret_key,
            api_version=api_version,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.config.validate()

        self._http_client = HTTPClient(self.config)
        self.payments = PaymentResource(self._http_client)
        self.webhooks = WebhookResource()  # No HTTP client needed

    @property
    def is_live_mode(self) -> bool:
        """Check if client is in live mode (실제 환경 여부 확인)."""
        return self.config.is_live_mode

    @property
    def is_test_mode(self) -> bool:
        """Check if client is in test mode (테스트 환경 여부 확인)."""
        return self.config.is_test_mode
