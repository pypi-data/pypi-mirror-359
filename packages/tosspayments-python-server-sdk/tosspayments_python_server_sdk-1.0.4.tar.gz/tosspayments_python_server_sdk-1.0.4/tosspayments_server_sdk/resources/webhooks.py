import json
from typing import Union

from tosspayments_server_sdk.exceptions import WebhookVerificationError
from tosspayments_server_sdk.models.webhook import WebhookEvent, create_webhook_event


class WebhookResource:

    def verify_and_parse(
        self,
        payload: Union[str, bytes],
    ) -> WebhookEvent:
        try:
            if isinstance(payload, bytes):
                payload_str = payload.decode("utf-8")
            else:
                payload_str = payload

            webhook_data = json.loads(payload_str)

            return create_webhook_event(webhook_data)

        except json.JSONDecodeError as e:
            raise WebhookVerificationError(f"Invalid JSON payload: {str(e)}")
        except Exception as e:
            raise WebhookVerificationError(f"Webhook verification failed: {str(e)}")
