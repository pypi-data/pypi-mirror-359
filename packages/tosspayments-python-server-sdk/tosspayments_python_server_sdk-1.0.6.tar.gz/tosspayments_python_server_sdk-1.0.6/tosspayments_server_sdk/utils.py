from typing import Dict, Any


def verify_payment_webhook_secret(
    webhook_data: Dict[str, Any],
    expected_secret: str,
) -> bool:
    """verify secret value for payment webhook (only for DEPOSIT_CALLBACK)

    Args:
        webhook_data (Dict[str, Any]): webhook event body (웹훅 이벤트 본문)
        expected_secret (str): secret (결제 승인 시 받은 secret 값)
    """
    webhook_secret = webhook_data.get("secret")
    return webhook_secret == expected_secret
