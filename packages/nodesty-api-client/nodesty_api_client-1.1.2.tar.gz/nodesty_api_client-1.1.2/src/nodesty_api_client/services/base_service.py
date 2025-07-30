from abc import ABC
from typing import Dict, TypeVar, Type, Optional
from httpx import AsyncClient, HTTPStatusError

from src.nodesty_api_client.models.shared import ApiResponse

T = TypeVar('T')

class BaseApiService(ABC):

    def __init__(self, client: AsyncClient, base_url: str, access_token: str):
        self._client = client
        self._base_url = base_url
        self._access_token = access_token

    def _get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"PAT {self._access_token}"}

    async def _make_request(
            self,
            method: str,
            url: str,
            response_type: Type[T],
            **kwargs
    ) -> ApiResponse[T]:
        try:
            response = await self._client.request(
                method,
                url,
                headers=self._get_headers(),
                **kwargs
            )
            response.raise_for_status()

            response_data = response.json() if response.content else []

            return ApiResponse[response_type].model_validate(response_data)

        except HTTPStatusError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except:
                pass

            error_response = {
                "error": error_data.get("message", f"HTTP {e.response.status_code}: {e.response.reason_phrase}"),
                "data": None
            }
            return ApiResponse[response_type].model_validate(error_response)

        except Exception as e:
            error_response = {
                "error": str(e),
                "data": None
            }
            return ApiResponse[response_type].model_validate(error_response)

    async def _get(self, endpoint: str, response_type: Type[T], **kwargs) -> ApiResponse[T]:
        url = f"{self._base_url}{endpoint}"
        return await self._make_request("GET", url, response_type, **kwargs)

    async def _post(self, endpoint: str, response_type: Type[T], data: Optional[Dict] = None, **kwargs) -> ApiResponse[T]:
        url = f"{self._base_url}{endpoint}"
        if data:
            kwargs['json'] = data
        return await self._make_request("POST", url, response_type, **kwargs)

    async def _put(self, endpoint: str, response_type: Type[T], data: Optional[Dict] = None, **kwargs) -> ApiResponse[T]:
        url = f"{self._base_url}{endpoint}"
        if data:
            kwargs['json'] = data
        return await self._make_request("PUT", url, response_type, **kwargs)

    async def _delete(self, endpoint: str, response_type: Type[T], **kwargs) -> ApiResponse[T]:
        url = f"{self._base_url}{endpoint}"
        return await self._make_request("DELETE", url, response_type, **kwargs)