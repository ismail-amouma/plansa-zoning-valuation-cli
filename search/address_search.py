

from __future__ import annotations
import json
from models import Address_Search
from curl_cffi.requests import AsyncSession
from search.address_search_erros import (
    AddressServiceError,
    AddressParseError,
    AddressNotFoundError
)
from parsers import _strip_jsonp, _JSONP_CALLBACK





async def get_address(session: AsyncSession, address: str) -> Address_Search:
    """Fetch address details from the remote geocoder.

    Raises one of the custom *Address* exceptions defined above.
    """
    url = (
        "https://lsa1.geohub.sa.gov.au/"
        "arcgis/rest/services/Locators/SAGAF_Valuation/"
        "GeocodeServer/findAddressCandidates"
    )

    params = {
        "Single Line Input": address,
        "outFields": "Valuation",
        "f": "json",
        "callback": _JSONP_CALLBACK,
    }

    try:
        response = await session.get(url, params=params, impersonate="chrome")
    except Exception as exc:  # transport error
        raise AddressServiceError(msg="Couldn't reach address service.", detail=exc) from exc

    if getattr(response, "status_code", None) != 200:
        raise AddressServiceError(status_code=response.status_code, detail=response.text)

    raw_body = response.text
    try:
        json_text = _strip_jsonp(raw_body)
        data = json.loads(json_text)
    except AddressParseError:
        raise
    except Exception as exc:  
        raise AddressParseError(detail=raw_body[:500]) from exc

    candidates = data.get("candidates") or []
    if not candidates:
        raise AddressNotFoundError(address)

    candidate = candidates[0]
    try:
        return Address_Search(
            full_address=candidate["address"],
            latitude=candidate["location"]["y"],
            longitude=candidate["location"]["x"],
            Valuation=candidate["attributes"]["Valuation"],
        )
    except Exception as exc:
        raise AddressParseError(detail=candidate) from exc



