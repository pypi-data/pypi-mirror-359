# TossPayments Python Server SDK

[![PyPI version](https://badge.fury.io/py/tosspayments-python-server-sdk.svg)](https://badge.fury.io/py/tosspayments-python-server-sdk)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for TossPayments API integration, designed to make server-side payment processing simple and intuitive.

> **Note**  
> This is an unofficial SDK for TossPayments API. All features are implemented based on the official TossPayments API documentation (v1) and sample data provided in the official documentation.

## Installation

```bash
pip install tosspayments-python-server-sdk
```

## Quick Start

### Initialize Client

```python
from tosspayments_server_sdk import Client

# Test environment
client = Client(secret_key="test_sk_...")

# Live environment  
client = Client(secret_key="live_sk_...")
```

### Confirm Payment

```python
try:
    payment = client.payments.confirm(
        payment_key="5zJ4xY7m0kODnyRpQWGrN2xqGlNvLrKwv1M9ENjbeoPaZdL6",
        order_id="a4CWyWY5m89PNh7xJwhk1",
        amount=15000
    )
    
    print(f"Payment completed: {payment.order_name}")
    print(f"Amount: {payment.total_amount:,} KRW")
    
except tosspayments_server_sdk.APIError as e:
    print(f"Payment failed: {e.message}")
```

### Retrieve Payment

```python
# Retrieve by payment key
payment = client.payments.retrieve("5zJ4xY7m0kODnyRpQWGrN2xqGlNvLrKwv1M9ENjbeoPaZdL6")

# Retrieve by order ID
payment = client.payments.retrieve_by_order_id("a4CWyWY5m89PNh7xJwhk1")

print(f"Payment status: {payment.status.value}")
print(f"Payment method: {payment.method}")
```

### Cancel Payment

```python
# Full cancellation
canceled_payment = client.payments.cancel(
    payment_key="5zJ4xY7m0kODnyRpQWGrN2xqGlNvLrKwv1M9ENjbeoPaZdL6",
    cancel_reason="Customer request"
)

# Partial cancellation
canceled_payment = client.payments.cancel(
    payment_key="5zJ4xY7m0kODnyRpQWGrN2xqGlNvLrKwv1M9ENjbeoPaZdL6",
    cancel_reason="Partial refund",
    cancel_amount=5000
)

print(f"Canceled amount: {canceled_payment.get_canceled_amount():,} KRW")
```

### Handle Webhooks

```python
from tosspayments_server_sdk import WebhookVerificationError

def handle_webhook(request):
    try:
        # Parse webhook data
        webhook_event = client.webhooks.verify_and_parse(request.body)
        
        if webhook_event.is_payment_event:
            payment_event = webhook_event
            print(f"Payment status changed: {payment_event.payment_key}")
            print(f"New status: {payment_event.status.value}")
            
            if payment_event.is_payment_completed():
                # Handle payment completion
                pass
                
        elif webhook_event.is_cancel_event:
            cancel_event = webhook_event  
            print(f"Cancellation completed: {cancel_event.transaction_key}")
            
    except WebhookVerificationError as e:
        print(f"Webhook verification failed: {e}")
        return "Bad Request", 400
        
    return "OK", 200
```

## Features

### 🔐 Authentication
- Automatic test/live environment detection
- Secure Basic Auth with API keys

### 💳 Payment Management
- Payment confirmation (`confirm`)
- Payment retrieval (`retrieve`, `retrieve_by_order_id`) 
- Payment cancellation (`cancel`)

### 🔔 Webhook Handling
- Payment status change events
- Cancellation status change events  
- Virtual account deposit completion events

### ⚡ HTTP Client
- Automatic retry with backoff
- Configurable timeout settings

## Configuration

```python
client = Client(
    secret_key="test_sk_...",
    api_version="v1",           # API version (default: v1)
    timeout=30,                 # Timeout in seconds (default: 30)
    max_retries=3               # Max retry attempts (default: 3)
)

# Environment check
print(f"Test mode: {client.is_test_mode}")
print(f"Live mode: {client.is_live_mode}")
```

## Requirements

- Python 3.9+

## Dependencies

- `requests>=2.28.0`

## License

MIT License

## Support

- [TossPayments Developer Documentation](https://docs.tosspayments.com/reference)
- [GitHub Issues](https://github.com/jhwang0801/tosspayments-python-server-sdk/issues)

## Changelog

### 1.0.2 (2025-07-02)
- Complete internationalization (English-first with Korean support)
- Enhanced documentation with detailed guides
- Improved type safety and code documentation
- Added comprehensive documentation site
- Better PyPI package metadata

### 1.0.1 (2025-07-02)
- Version synchronization fix

### 1.0.0 (2025-06-05)
- Initial release
- Payment confirmation, retrieval, and cancellation features
- Webhook handling functionality

---

# 한국어 안내

## 토스페이먼츠 Python 서버 SDK

이 라이브러리는 토스페이먼츠 API를 Python 서버 환경에서 보다 편리하게 활용할 수 있도록 개발된 서드파티 SDK입니다.

### 주요 기능

- **결제 승인**: 클라이언트에서 받은 결제 정보를 서버에서 승인
- **결제 조회**: 결제키 또는 주문번호로 결제 정보 조회
- **결제 취소**: 전체 또는 부분 결제 취소
- **웹훅 처리**: 결제 상태 변경 시 실시간 알림 처리

### 설치 및 사용법

자세한 사용법은 [문서 사이트](https://jhwang0801.github.io/tosspayments-python-server-sdk)를 참고하세요.

### 문의 및 지원

- [GitHub Issues](https://github.com/jhwang0801/tosspayments-python-server-sdk/issues)에서 문의사항을 남겨주세요.
- 토스페이먼츠 공식 API 문서는 [여기](https://docs.tosspayments.com/reference)에서 확인할 수 있습니다.

### 라이센스

MIT 라이센스 하에 배포됩니다.