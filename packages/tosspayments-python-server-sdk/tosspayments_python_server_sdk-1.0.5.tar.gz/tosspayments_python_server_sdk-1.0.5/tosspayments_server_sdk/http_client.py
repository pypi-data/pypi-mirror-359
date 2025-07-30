import json
from typing import Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter

from tosspayments_server_sdk.auth import Auth
from tosspayments_server_sdk.config import Config
from urllib3.util.retry import Retry

from tosspayments_server_sdk.error_codes import ErrorCodes
from tosspayments_server_sdk.exceptions import APIError, RateLimitError, NetworkError


class HTTPClient:

    def __init__(self, config: Config):
        self.config = config
        self.auth = Auth(config.secret_key)
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        session = requests.Session()

        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=[500, 502, 503, 504],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)

        return session

    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.config.api_url}/{path.lstrip('/')}"

        request_headers = self.auth.get_headers()
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=data,
                headers=request_headers,
                timeout=self.config.timeout,
            )

            return self._handle_response(response)

        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timeout: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Request failed: {e}") from e

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {}

        if 200 <= response.status_code < 300:
            return response_data

        error_code = response_data.get("code", "UNKNOWN_ERROR")
        error_message = response_data.get("message", "Unknown error occurred")

        if ErrorCodes.is_auth_error(error_code):
            from .exceptions import AuthenticationError

            raise AuthenticationError(f"Authentication failed: {error_message}")

        elif response.status_code == 429:
            raise RateLimitError(
                error_message, error_code, response.status_code, response_data
            )

        elif response.status_code == 404:
            from .exceptions import PaymentNotFoundError

            raise PaymentNotFoundError(
                error_message, error_code, response.status_code, response_data
            )

        else:
            raise APIError(
                error_message, error_code, response.status_code, response_data
            )

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._make_request("GET", path, params=params)

    def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._make_request("POST", path, data=data)

    def put(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._make_request("PUT", path, data=data)

    def delete(self, path: str) -> Dict[str, Any]:
        return self._make_request("DELETE", path)
