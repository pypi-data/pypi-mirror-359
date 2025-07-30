from unittest.mock import patch

import pytest

from tosspayments_server_sdk.exceptions import ValidationError
from tosspayments_server_sdk.models.enums import PaymentStatus
from tosspayments_server_sdk.models.payment import Payment


class TestPaymentResource:
    @patch("tosspayments_server_sdk.client.HTTPClient.get")
    def test_retrieve_payment_success(self, mock_get, toss_client, mock_payment_data):
        mock_get.return_value = mock_payment_data
        _test_payment_key = "5EnNZRJGvaBX7zk2yd8ydw26XvwXkLrx9POLqKQjmAw4b0e1"
        _test_order_id = "a4CWyWY5m89PNh7xJwhk1"
        _test_amount = 1000

        payment = toss_client.payments.retrieve(_test_payment_key)

        assert isinstance(payment, Payment)
        assert payment.payment_key == _test_payment_key
        assert payment.status == PaymentStatus.DONE
        assert payment.total_amount == _test_amount

        mock_get.assert_called_once_with(f"payments/{_test_payment_key}")

    def test_retrieve_payment_with_empty_key(self, toss_client):
        with pytest.raises(ValidationError, match="payment_key is required"):
            toss_client.payments.retrieve("")

    @patch("tosspayments_server_sdk.client.HTTPClient.get")
    def test_retrieve_by_order_id_success(
        self, mock_get, toss_client, mock_payment_data
    ):
        mock_get.return_value = mock_payment_data
        _test_payment_key = "5EnNZRJGvaBX7zk2yd8ydw26XvwXkLrx9POLqKQjmAw4b0e1"
        _test_order_id = "a4CWyWY5m89PNh7xJwhk1"
        _test_amount = 1000

        payment = toss_client.payments.retrieve_by_order_id(_test_order_id)

        assert isinstance(payment, Payment)
        assert payment.order_id == _test_order_id
        assert payment.status == PaymentStatus.DONE
        assert payment.total_amount == _test_amount

        mock_get.assert_called_once_with(f"payments/orders/{_test_order_id}")

    @patch("tosspayments_server_sdk.client.HTTPClient.post")
    def test_confirm_payment_success(self, mock_post, toss_client, mock_payment_data):
        mock_post.return_value = mock_payment_data
        _test_payment_key = "5EnNZRJGvaBX7zk2yd8ydw26XvwXkLrx9POLqKQjmAw4b0e1"
        _test_order_id = "a4CWyWY5m89PNh7xJwhk1"
        _test_amount = 1000

        payment = toss_client.payments.confirm(
            payment_key=_test_payment_key,
            order_id=_test_order_id,
            amount=_test_amount,
        )

        assert isinstance(payment, Payment)
        assert payment.is_paid() is True

        mock_post.assert_called_once_with(
            "payments/confirm",
            {
                "paymentKey": _test_payment_key,
                "orderId": _test_order_id,
                "amount": _test_amount,
            },
        )

    def test_confirm_payment_validation_errors(self, toss_client):
        _test_payment_key = "5EnNZRJGvaBX7zk2yd8ydw26XvwXkLrx9POLqKQjmAw4b0e1"
        _test_order_id = "a4CWyWY5m89PNh7xJwhk1"
        _test_amount = 1000

        with pytest.raises(ValidationError, match="payment_key is required"):
            toss_client.payments.confirm("", _test_order_id, _test_amount)

        with pytest.raises(ValidationError, match="order_id is required"):
            toss_client.payments.confirm(_test_payment_key, "", _test_amount)

        with pytest.raises(ValidationError, match="amount must be positive"):
            toss_client.payments.confirm(_test_payment_key, _test_order_id, 0)

    @patch("tosspayments_server_sdk.client.HTTPClient.post")
    def test_cancel_payment_success(self, mock_post, toss_client, mock_cancel_data):
        mock_post.return_value = mock_cancel_data
        _test_payment_key = "5EnNZRJGvaBX7zk2yd8ydw26XvwXkLrx9POLqKQjmAw4b0e1"
        _test_order_id = "a4CWyWY5m89PNh7xJwhk1"
        _test_amount = 1000

        payment = toss_client.payments.cancel(
            payment_key=_test_payment_key,
            cancel_reason="테스트 결제 취소",
        )

        assert payment.status == PaymentStatus.CANCELED
        assert payment.balance_amount == 0
        assert len(payment.cancels) == 1

        mock_post.assert_called_once_with(
            f"payments/{_test_payment_key}/cancel",
            {"cancelReason": "테스트 결제 취소"},
        )

    def test_cancel_payment_validation_errors(self, toss_client):
        _test_payment_key = "5EnNZRJGvaBX7zk2yd8ydw26XvwXkLrx9POLqKQjmAw4b0e1"
        _test_order_id = "a4CWyWY5m89PNh7xJwhk1"
        _test_amount = 1000

        with pytest.raises(ValidationError, match="payment_key is required"):
            toss_client.payments.cancel("", "테스트 결제 취소")

        with pytest.raises(ValidationError, match="cancel_reason is required"):
            toss_client.payments.cancel(_test_payment_key, "")

        with pytest.raises(ValidationError, match="cancel_amount must be positive"):
            toss_client.payments.cancel(
                _test_payment_key, "테스트 결제 취소", cancel_amount=0
            )
