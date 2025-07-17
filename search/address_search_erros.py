from __future__ import annotations
from typing import Any, Optional

class AddressSearchError(Exception):
    """Base error for address lookups."""

    default_msg = "Address lookup failed."

    def __init__(self, msg: Optional[str] = None, *, detail: Any = None):
        super().__init__(msg or self.default_msg)
        self.detail = detail  


class AddressServiceError(AddressSearchError):
    """Remote geocoder service problem (HTTP error, network failure, etc.)."""

    default_msg = "Address service is unavailable. Please try again."

    def __init__(self, status_code: Optional[int] = None, msg: Optional[str] = None, *, detail: Any = None):
        super().__init__(msg or self.default_msg, detail=detail)
        self.status_code = status_code


class AddressParseError(AddressSearchError):
    """We contacted the service but couldn't understand its response."""

    default_msg = "Problem reading address service response."


class AddressNotFoundError(AddressSearchError):
    """The service responded successfully but had no candidates."""

    def __init__(self, address: str, msg: Optional[str] = None, *, detail: Any = None):
        super().__init__(msg or f"No results for: {address}", detail=detail)
        self.address = address
