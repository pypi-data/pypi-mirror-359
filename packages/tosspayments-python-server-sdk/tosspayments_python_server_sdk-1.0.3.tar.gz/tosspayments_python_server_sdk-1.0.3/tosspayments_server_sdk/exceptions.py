from typing import Optional, Dict, Any


class TossPaymentsError(Exception):
    """Base class for all TossPayments SDK exceptions"""

    pass


class APIError(TossPaymentsError):
    """Error that occurs during API calls"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.response_data = response_data or {}

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class WebhookVerificationError(TossPaymentsError):
    """Webhook parsing failure error"""

    pass


class AuthenticationError(TossPaymentsError):
    """Authentication related error"""

    pass


class ValidationError(TossPaymentsError):
    """Input validation error"""

    pass


class NetworkError(TossPaymentsError):
    """Network related error"""

    pass


class RateLimitError(APIError):
    """API request limit exceeded"""

    pass


class PaymentNotFoundError(APIError):
    """Payment information not found"""

    pass
