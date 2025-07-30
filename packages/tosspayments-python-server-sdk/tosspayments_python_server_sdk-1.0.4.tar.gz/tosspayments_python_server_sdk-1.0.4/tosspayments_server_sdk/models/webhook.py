from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Union

from tosspayments_server_sdk.exceptions import ValidationError
from tosspayments_server_sdk.models.base import BaseModel
from tosspayments_server_sdk.models.enums import PaymentStatus
from tosspayments_server_sdk.models.payment import Payment, Cancellation


@dataclass
class BaseWebhookEvent(BaseModel, ABC):
    created_at: datetime
    event_type: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseWebhookEvent":

        if "eventType" in data:
            event_type = data["eventType"]

            if event_type == "PAYMENT_STATUS_CHANGED":
                return PaymentStatusChangedEvent.from_dict(data)
            elif event_type == "CANCEL_STATUS_CHANGED":
                return CancelStatusChangedEvent.from_dict(data)
            else:
                raise ValidationError(f"Unsupported webhook event type: {event_type}")

        elif "secret" in data and "transactionKey" in data:
            return DepositCallbackEvent.from_dict(data)

        else:
            raise ValidationError(
                "Unable to determine webhook event type from payload structure"
            )

    @property
    def is_payment_event(self) -> bool:
        return self.event_type == "PAYMENT_STATUS_CHANGED"

    @property
    def is_cancel_event(self) -> bool:
        return self.event_type == "CANCEL_STATUS_CHANGED"

    @property
    def is_virtual_account_event(self) -> bool:
        return self.event_type == "DEPOSIT_CALLBACK"


@dataclass
class PaymentStatusChangedEvent(BaseWebhookEvent):
    payment: Payment  # Payment object parsed from webhook data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PaymentStatusChangedEvent":
        """

        Args:
            data: {
                "eventType": "PAYMENT_STATUS_CHANGED",
                "createdAt": "2022-01-01T00:00:00.000000",
                "data": { ...payment dict... }
            }
        """

        created_at = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
        payment = Payment.from_dict(data["data"])

        return cls(
            created_at=created_at,
            event_type="PAYMENT_STATUS_CHANGED",
            payment=payment,
        )

    @property
    def payment_key(self) -> str:
        return self.payment.payment_key

    @property
    def order_id(self) -> str:
        return self.payment.order_id

    @property
    def status(self) -> PaymentStatus:
        return self.payment.status

    def is_payment_completed(self) -> bool:
        return self.payment.is_paid()

    def is_payment_canceled(self) -> bool:
        return self.payment.is_canceled()


@dataclass
class CancelStatusChangedEvent(BaseWebhookEvent):
    cancellation: Cancellation  # Cancellation object parsed from webhook data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CancelStatusChangedEvent":
        """

        Args:
            data: {
                "eventType": "CANCEL_STATUS_CHANGED",
                "createdAt": "2022-01-01T00:00:00.000000",
                "data": { ...cancellation dict... }
            }
        """
        created_at = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
        cancellation = Cancellation.from_dict(data["data"])

        return cls(
            created_at=created_at,
            event_type="CANCEL_STATUS_CHANGED",
            cancellation=cancellation,
        )

    @property
    def cancel_amount(self) -> int:
        return self.cancellation.cancel_amount

    @property
    def cancel_reason(self) -> str:
        return self.cancellation.cancel_reason

    @property
    def transaction_key(self) -> str:
        return self.cancellation.transaction_key


@dataclass
class DepositCallbackEvent(BaseWebhookEvent):
    secret: str  # Webhook verification secret
    status: PaymentStatus  # Deposit status
    transaction_key: str  # Transaction identifier
    order_id: str  # Order identifier

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DepositCallbackEvent":
        """

        Args:
            data: {
                "createdAt": "2022-01-01T00:00:00.000000",
                "secret": "2Qyln1ZAewT4hcqV8lgbn",
                "status": "DONE",
                "transactionKey": "9FF15E1A29D0E77C218F57262BFA4986",
                "orderId": "wVWsdzOISR3-AyrmAv3qK"
            }
        """
        created_at = datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00"))
        return cls(
            created_at=created_at,
            event_type="DEPOSIT_CALLBACK",
            secret=data["secret"],
            status=PaymentStatus(data["status"]),
            transaction_key=data["transactionKey"],
            order_id=data["orderId"],
        )

    def is_deposit_completed(self) -> bool:
        return self.status == PaymentStatus.DONE


WebhookEvent = Union[
    PaymentStatusChangedEvent,
    DepositCallbackEvent,
    CancelStatusChangedEvent,
]


def create_webhook_event(data: Dict[str, Any]) -> WebhookEvent:
    """Create event object from webhook data

    Args:
        data: Raw webhook data

    Returns:
        WebhookEvent: Webhook event object matching the event type

    Raises:
        ValidationError: When webhook type is unsupported or structure is unrecognizable
    """

    return BaseWebhookEvent.from_dict(data)  # type: ignore
