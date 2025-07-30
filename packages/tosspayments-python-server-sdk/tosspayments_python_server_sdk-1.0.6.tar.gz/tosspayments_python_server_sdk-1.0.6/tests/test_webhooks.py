import json

import pytest

from tosspayments_server_sdk.exceptions import WebhookVerificationError
from tosspayments_server_sdk.models.enums import PaymentStatus
from tosspayments_server_sdk.models.webhook import (
    PaymentStatusChangedEvent,
    DepositCallbackEvent,
    CancelStatusChangedEvent,
)


class TestWebhookResource:

    def test_verify_and_parse_payment_webhook_success(
        self, toss_client, mock_payment_data
    ):
        webhook_data = {
            "eventType": "PAYMENT_STATUS_CHANGED",
            "createdAt": "2022-01-01T00:00:00.000000",
            "data": mock_payment_data,
        }
        payload = json.dumps(webhook_data)

        event = toss_client.webhooks.verify_and_parse(payload)

        assert isinstance(event, PaymentStatusChangedEvent)
        assert event.event_type == "PAYMENT_STATUS_CHANGED"
        assert event.payment_key == "5EnNZRJGvaBX7zk2yd8ydw26XvwXkLrx9POLqKQjmAw4b0e1"
        assert event.order_id == "a4CWyWY5m89PNh7xJwhk1"
        assert event.status == PaymentStatus.DONE
        assert event.is_payment_completed() is True
        assert event.is_payment_event is True

    def test_verify_and_parse_deposit_webhook_success(self, toss_client):
        webhook_data = {
            "createdAt": "2022-01-01T00:00:00.000000",
            "secret": "DmKQbGzQQcVE3UoFNqWxL",
            "status": "DONE",
            "transactionKey": "9FF15E1A29D0E77C218F57262BFA4986",
            "orderId": "EbUYmJ4Q9EANnTWta8dok",
        }
        payload = json.dumps(webhook_data)

        event = toss_client.webhooks.verify_and_parse(payload)

        assert isinstance(event, DepositCallbackEvent)
        assert event.event_type == "DEPOSIT_CALLBACK"
        assert event.secret == "DmKQbGzQQcVE3UoFNqWxL"
        assert event.status == PaymentStatus.DONE
        assert event.transaction_key == "9FF15E1A29D0E77C218F57262BFA4986"
        assert event.order_id == "EbUYmJ4Q9EANnTWta8dok"
        assert event.is_deposit_completed() is True
        assert event.is_virtual_account_event is True

    def test_verify_and_parse_cancel_webhook_success(self, toss_client):
        webhook_data = {
            "eventType": "CANCEL_STATUS_CHANGED",
            "createdAt": "2024-02-13T12:20:23+09:00",
            "data": {
                "transactionKey": "090A796806E726BBB929F4A2CA7DB9A7",
                "cancelReason": "테스트 결제 취소",
                "taxExemptionAmount": 0,
                "canceledAt": "2024-02-13T12:20:23+09:00",
                "transferDiscountAmount": 0,
                "easyPayDiscountAmount": 0,
                "receiptKey": None,
                "cancelAmount": 1000,
                "taxFreeAmount": 0,
                "refundableAmount": 0,
                "cancelStatus": "DONE",
                "cancelRequestId": None,
            },
        }
        payload = json.dumps(webhook_data)

        event = toss_client.webhooks.verify_and_parse(payload)

        assert isinstance(event, CancelStatusChangedEvent)
        assert event.event_type == "CANCEL_STATUS_CHANGED"
        assert event.cancel_amount == 1000
        assert event.cancel_reason == "테스트 결제 취소"
        assert event.transaction_key == "090A796806E726BBB929F4A2CA7DB9A7"
        assert event.is_cancel_event is True

    def test_verify_and_parse_invalid_json(self, toss_client):
        invalid_payload = "invalid json"

        with pytest.raises(WebhookVerificationError, match="Invalid JSON payload"):
            toss_client.webhooks.verify_and_parse(invalid_payload)

    def test_verify_and_parse_unsupported_event_type(self, toss_client):
        unsupported_data = {
            "eventType": "UNSUPPORTED_EVENT",
            "createdAt": "2024-02-13T12:18:14+09:00",
            "data": {},
        }
        payload = json.dumps(unsupported_data)

        with pytest.raises(
            WebhookVerificationError, match="Webhook verification failed"
        ):
            toss_client.webhooks.verify_and_parse(payload)
