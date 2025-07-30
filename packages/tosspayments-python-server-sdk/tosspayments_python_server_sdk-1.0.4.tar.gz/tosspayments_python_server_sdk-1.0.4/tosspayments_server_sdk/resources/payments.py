from typing import Optional, Dict

from tosspayments_server_sdk.exceptions import ValidationError
from tosspayments_server_sdk.models.payment import Payment
from tosspayments_server_sdk.resources.base import BaseResource


class PaymentResource(BaseResource):
    """Payment API Resource (결제 API 리소스)

    Official docs: https://docs.tosspayments.com/reference#paymentkey
    """

    def retrieve(self, payment_key: str) -> Payment:
        """Retrieve a payment using the paymentKey (결제키로 결제 조회)

        Args:
            payment_key (str): Payment key (결제 키)

        Returns:
            Payment: Payment object (결제 정보)
        """
        if not payment_key:
            raise ValidationError("payment_key is required")

        response_data = self._client.get(f"payments/{payment_key}")
        return Payment.from_dict(response_data)

    def retrieve_by_order_id(self, order_id: str) -> Payment:
        """Retrieve a payment using the orderId (주문번호로 결제 조회)

        Args:
            order_id (str): Order ID (주문 ID)

        Returns:
            Payment: Payment object (결제 정보)
        """
        if not order_id:
            raise ValidationError("order_id is required")

        response_data = self._client.get(f"payments/orders/{order_id}")
        return Payment.from_dict(response_data)

    def confirm(self, payment_key: str, order_id: str, amount: int) -> Payment:
        """Confirm a payment (결제 승인)

        Args:
            payment_key (str): Payment key (결제 키)
            order_id (str): Order ID (주문 ID)
            amount (int): Amount to charge (결제 금액)

        Returns:
            Payment: Payment object (결제 정보)
        """
        if not payment_key:
            raise ValidationError("payment_key is required")
        if not order_id:
            raise ValidationError("order_id is required")
        if not amount or amount <= 0:
            raise ValidationError("amount must be positive")

        data = {
            "paymentKey": payment_key,
            "orderId": order_id,
            "amount": amount,
        }

        response_data = self._client.post("payments/confirm", data)
        return Payment.from_dict(response_data)

    def cancel(
        self,
        payment_key: str,
        cancel_reason: str,
        cancel_amount: Optional[int] = None,
        refund_receive_account: Optional[Dict[str, str]] = None,
        tax_free_amount: Optional[int] = None,
    ) -> Payment:
        """Cancel a payment (결제 취소)

        Args:
            payment_key (str): Payment key (결제 키)
            cancel_reason (str): Reason for cancellation (취소 사유)
            cancel_amount (int, optional): Amount to cancel (취소 금액)
            refund_receive_account (dict, optional): Customer's refund account info (환불 계좌 정보)
            tax_free_amount (int, optional): Tax-free amount (면세 금액)

        Returns:
            Payment: Payment object (결제 정보)
        """
        if not payment_key:
            raise ValidationError("payment_key is required")
        if not cancel_reason:
            raise ValidationError("cancel_reason is required")
        if cancel_amount is not None and cancel_amount <= 0:
            raise ValidationError("cancel_amount must be positive")

        data = {"cancelReason": cancel_reason}

        if cancel_amount is not None:
            data["cancelAmount"] = cancel_amount
        if refund_receive_account:
            data["refundReceiveAccount"] = refund_receive_account
        if tax_free_amount is not None:
            data["taxFreeAmount"] = tax_free_amount

        response_data = self._client.post(f"payments/{payment_key}/cancel", data)
        return Payment.from_dict(response_data)

    # def request_virtual_account(self):
    #     pass
