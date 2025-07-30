from dataclasses import dataclass


@dataclass
class Config:
    # Auth
    secret_key: str

    # TossPayments API settings
    api_base: str = "https://api.tosspayments.com"
    api_version: str = "v1"

    # HTTP settings
    timeout: int = 30
    max_retries: int = 3
    backoff_factor: float = 0.5

    @property
    def api_url(self) -> str:
        """Get complete API URL (전체 API URL 조회)."""
        return f"{self.api_base.rstrip('/')}/{self.api_version}"

    @property
    def is_live_mode(self) -> bool:
        """Check if in live mode (실제 환경 여부 확인)."""
        return self.secret_key.startswith("live_sk")

    @property
    def is_test_mode(self) -> bool:
        """Check if in test mode (테스트 환경 여부 확인)."""
        return self.secret_key.startswith("test_sk")

    def validate(self):
        """Validate configuration (설정 검증)."""
        if not self.secret_key:
            raise ValueError("secret_key is required")

        if not self.secret_key.startswith(("test_sk", "live_sk")):
            raise ValueError("secret_key must start with 'test_sk' or 'live_sk'")

        if self.timeout <= 0:
            raise ValueError("timeout must be positive")

        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
