from datetime import timedelta
from typing import TypeVar, Generic, Optional, Union

from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    error: Optional[str] = None
    data: Optional[T] = None


class RestClientOptions(BaseModel):
    access_token: str
    base_url: str = "https://nodesty.com/api"
    retry: int = 3
    timeout: int = 30
    rate_limit_offset: int = 50

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, access_token: str, **data):
        super().__init__(access_token=access_token, **data)

    def with_base_url(self, base_url: str) -> 'RestClientOptions':
        self.base_url = base_url
        return self

    def with_retry(self, retry: int) -> 'RestClientOptions':
        self.retry = retry
        return self

    def with_timeout(self, timeout: Union[int, timedelta]) -> 'RestClientOptions':
        if isinstance(timeout, timedelta):
            self.timeout = int(timeout.total_seconds())
        else:
            self.timeout = timeout
        return self

    def with_rate_limit_offset(self, offset: Union[int, timedelta]) -> 'RestClientOptions':
        if isinstance(offset, timedelta):
            self.rate_limit_offset = int(offset.total_milliseconds())
        else:
            self.rate_limit_offset = offset
        return self
