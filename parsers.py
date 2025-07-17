from search.address_search_erros import AddressParseError





_JSONP_CALLBACK = "angular.callbacks._5"  


def _strip_jsonp(text: str, callback: str = _JSONP_CALLBACK) -> str:
    """Extract the JSON payload from a JSONP response body.

    Raises AddressParseError if we can't isolate a JSON object.
    """
    prefix = f"{callback}("
    suffix = ")"
    try:
        start = text.index(prefix) + len(prefix)
        end = text.rindex(suffix)
    except ValueError as exc:  
        raise AddressParseError(detail=text[:500]) from exc
    return text[start:end]