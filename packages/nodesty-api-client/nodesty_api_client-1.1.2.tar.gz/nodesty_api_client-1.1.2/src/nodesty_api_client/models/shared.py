from datetime import timedelta
from typing import Generic, TypeVar, Optional, Any, Dict, Union
from pydantic import BaseModel, Field, model_validator

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None

    @model_validator(mode='before')
    @classmethod
    def validate_response(cls, values: Any) -> Dict[str, Any]:
        if isinstance(values, dict):
            if not any(key in values for key in ['data', 'error', 'message']):
                return {'data': values}
        elif isinstance(values, list):
            return {'data': values}
        return values

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def is_error(self) -> bool:
        return self.error is not None

    def get_data_or_raise(self) -> T:
        if self.error:
            raise ValueError(self.error)
        return self.data

    def get_error_message(self) -> str:
        if self.is_success:
            return ""
        return self.error or "Unknown error occurred"

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
            self.rate_limit_offset = int(offset.total_seconds() * 1000)
        else:
            self.rate_limit_offset = offset
        return self