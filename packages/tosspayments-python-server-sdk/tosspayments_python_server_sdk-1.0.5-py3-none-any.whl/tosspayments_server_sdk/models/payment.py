from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List

from tosspayments_server_sdk.models.base import BaseModel
from tosspayments_server_sdk.models.enums import PaymentStatus, PaymentType


@dataclass
class Card(BaseModel):
    amount: int
    issuer_code: str
    acquirer_code: Optional[str] = None
    number: Optional[str] = None
    installment_plan_months: Optional[int] = None
    approve_no: Optional[str] = None
    use_card_point: Optional[bool] = None
    card_type: Optional[str] = None
    owner_type: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Card":
        return cls(
            amount=data["amount"],
            issuer_code=data["issuerCode"],
            acquirer_code=data.get("acquirerCode"),
            number=data.get("number"),
            installment_plan_months=data.get("installmentPlanMonths"),
            approve_no=data.get("approveNo"),
            use_card_point=data.get("useCardPoint"),
            card_type=data.get("cardType"),
            owner_type=data.get("ownerType"),
        )


@dataclass
class VirtualAccount(BaseModel):
    account_type: str
    account_number: str
    bank_code: str
    customer_name: str
    due_date: datetime
    refund_status: str
    expired: bool
    settled_amount: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VirtualAccount":
        return cls(
            account_type=data["accountType"],
            account_number=data["accountNumber"],
            bank_code=data["bankCode"],
            customer_name=data["customerName"],
            due_date=datetime.fromisoformat(data["dueDate"].replace("Z", "+00:00")),
            refund_status=data["refundStatus"],
            expired=data["expired"],
            settled_amount=data["settledAmount"],
        )


@dataclass
class Cancellation(BaseModel):
    cancel_amount: int
    cancel_reason: str
    canceled_at: datetime
    transaction_key: str
    receipt_key: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cancellation":
        return cls(
            cancel_amount=data["cancelAmount"],
            cancel_reason=data["cancelReason"],
            canceled_at=datetime.fromisoformat(
                data["canceledAt"].replace("Z", "+00:00")
            ),
            transaction_key=data["transactionKey"],
            receipt_key=data.get("receiptKey"),
        )


@dataclass
class Payment(BaseModel):
    # Mandatory Fields
    version: str
    payment_key: str
    type: PaymentType
    order_id: str
    order_name: str
    mid: str
    currency: str
    method: str
    total_amount: int
    balance_amount: int
    status: PaymentStatus
    requested_at: datetime

    # Optional Fields
    approved_at: Optional[datetime] = None
    use_escrow: bool = False
    last_transaction_key: Optional[str] = None
    supplied_amount: int = 0
    vat: int = 0
    cultural_expense: bool = False
    tax_free_amount: int = 0
    tax_exemption_amount: int = 0
    cancels: List[Cancellation] = field(default_factory=list)
    is_partial_cancelable: bool = True

    # Payment Method Information
    card: Optional[Card] = None
    virtual_account: Optional[VirtualAccount] = None
    mobile_phone: Optional[Dict[str, Any]] = None
    gift_certificate: Optional[Dict[str, Any]] = None
    transfer: Optional[Dict[str, Any]] = None
    receipt: Optional[Dict[str, Any]] = None
    easy_pay: Optional[Dict[str, Any]] = None

    # Additional Information
    country: str = "KR"
    failure: Optional[Dict[str, Any]] = None
    cash_receipt: Optional[Dict[str, Any]] = None
    discount: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Payment":
        # cancellations
        cancels = []
        if data.get("cancels"):
            cancels = [Cancellation.from_dict(cancel) for cancel in data["cancels"]]

        # card
        card = None
        if data.get("card"):
            card = Card.from_dict(data["card"])

        # virtual account
        virtual_account = None
        if data.get("virtualAccount"):
            virtual_account = VirtualAccount.from_dict(data["virtualAccount"])

        return cls(
            version=data["version"],
            payment_key=data["paymentKey"],
            type=PaymentType(data["type"]),
            order_id=data["orderId"],
            order_name=data["orderName"],
            mid=data["mId"],
            currency=data["currency"],
            method=data["method"],
            total_amount=data["totalAmount"],
            balance_amount=data["balanceAmount"],
            status=PaymentStatus(data["status"]),
            requested_at=datetime.fromisoformat(
                data["requestedAt"].replace("Z", "+00:00")
            ),
            approved_at=(
                datetime.fromisoformat(data["approvedAt"].replace("Z", "+00:00"))
                if data.get("approvedAt")
                else None
            ),
            use_escrow=data.get("useEscrow", False),
            last_transaction_key=data.get("lastTransactionKey"),
            supplied_amount=data.get("suppliedAmount", 0),
            vat=data.get("vat", 0),
            cultural_expense=data.get("culturalExpense", False),
            tax_free_amount=data.get("taxFreeAmount", 0),
            tax_exemption_amount=data.get("taxExemptionAmount", 0),
            cancels=cancels,
            is_partial_cancelable=data.get("isPartialCancelable", True),
            card=card,
            virtual_account=virtual_account,
            mobile_phone=data.get("mobilePhone"),
            gift_certificate=data.get("giftCertificate"),
            transfer=data.get("transfer"),
            receipt=data.get("receipt"),
            easy_pay=data.get("easyPay"),
            country=data.get("country", "KR"),
            failure=data.get("failure"),
            cash_receipt=data.get("cashReceipt"),
            discount=data.get("discount"),
        )

    def is_paid(self) -> bool:
        """Check if payment is completed (결제 완료 여부 확인)."""
        return self.status == PaymentStatus.DONE

    def is_canceled(self) -> bool:
        """Check if payment is canceled (결제 취소 여부 확인)."""
        return self.status in [PaymentStatus.CANCELED, PaymentStatus.PARTIAL_CANCELED]

    def get_cancelable_amount(self) -> int:
        """Get cancelable amount (취소 가능 금액 조회)."""
        return self.balance_amount

    def get_canceled_amount(self) -> int:
        """Get canceled amount (취소된 금액 조회)."""
        return self.total_amount - self.balance_amount

    def can_be_canceled(self) -> bool:
        """Check if payment can be canceled (취소 가능 여부 확인)."""
        return self.balance_amount > 0
