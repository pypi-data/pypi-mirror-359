from abc import ABC
from ..http_client import HTTPClient


class BaseResource(ABC):
    def __init__(self, http_client: HTTPClient):
        self._client = http_client
