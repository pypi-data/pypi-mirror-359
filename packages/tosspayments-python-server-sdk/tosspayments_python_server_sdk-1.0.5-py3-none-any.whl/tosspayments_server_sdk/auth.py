import base64
from typing import Dict


class Auth:
    """Authentication handler for TossPayments API (토스페이먼츠 API 인증 처리기)."""

    def __init__(self, secret_key: str):
        """Initialize auth with secret key (시크릿 키로 인증 초기화)."""
        self.secret_key = secret_key

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers (인증 헤더 조회)."""
        credentials = f"{self.secret_key}:"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }
