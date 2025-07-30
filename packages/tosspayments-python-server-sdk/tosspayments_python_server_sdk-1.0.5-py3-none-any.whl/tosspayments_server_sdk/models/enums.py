from enum import Enum


class PaymentStatus(Enum):
    """Payment status enumeration (결제 상태)"""

    READY = "READY"  # Payment ready (결제 준비)
    IN_PROGRESS = "IN_PROGRESS"  # Payment in progress (결제 진행 중)
    WAITING_FOR_DEPOSIT = "WAITING_FOR_DEPOSIT"  # Waiting for deposit (입금 대기)
    DONE = "DONE"  # Payment completed (결제 완료)
    CANCELED = "CANCELED"  # Payment canceled (결제 취소)
    PARTIAL_CANCELED = "PARTIAL_CANCELED"  # Partially canceled (부분 취소)
    ABORTED = "ABORTED"  # Payment aborted (결제 중단)
    EXPIRED = "EXPIRED"  # Payment expired (결제 만료)


class PaymentMethod(Enum):
    """Payment method enumeration (결제 수단)"""

    CARD = "카드"  # Card (카드)
    VIRTUAL_ACCOUNT = "가상계좌"  # Virtual account (가상계좌)
    SIMPLE_PAYMENT = "간편결제"  # Simple payment (간편결제)
    MOBILE_PHONE = "휴대폰"  # Mobile phone (휴대폰)
    ACCOUNT_TRANSFER = "계좌이체"  # Account transfer (계좌이체)
    CULTURE_GIFT_CERTIFICATE = "문화상품권"  # Culture gift certificate (문화상품권)
    BOOK_CULTURE_GIFT_CERTIFICATE = (
        "도서문화상품권"  # Book culture gift certificate (도서문화상품권)
    )
    GAME_CULTURE_GIFT_CERTIFICATE = (
        "게임문화상품권"  # Game culture gift certificate (게임문화상품권)
    )


class PaymentType(Enum):
    """Payment type enumeration (결제 유형)"""

    NORMAL = "NORMAL"  # Normal payment (일반결제)
    BILLING = "BILLING"  # Billing payment (자동결제)
    BRANDPAY = "BRANDPAY"  # Brand pay (브랜드페이)
