from httpx import AsyncClient

from src.nodesty_api_client.models import RestClientOptions
from src.nodesty_api_client.services import DedicatedServerApiService
from src.nodesty_api_client.services import FirewallApiService
from src.nodesty_api_client.services import UserApiService
from src.nodesty_api_client.services import VpsApiService


class NodestyApiClient:

    def __init__(self, options: RestClientOptions):
        self._options = options
        self._client = AsyncClient(
            timeout=self._options.timeout,
            base_url=self._options.base_url
        )

        self.user = UserApiService(self._client, self._options.base_url, self._options.access_token)
        self.vps = VpsApiService(self._client, self._options.base_url, self._options.access_token)
        self.firewall = FirewallApiService(self._client, self._options.base_url, self._options.access_token)
        self.dedicated_server = DedicatedServerApiService(self._client, self._options.base_url,
                                                          self._options.access_token)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        await self._client.aclose()

    @property
    def http_client(self) -> AsyncClient:
        return self._client
