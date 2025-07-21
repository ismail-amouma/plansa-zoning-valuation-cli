from search.address_search_erros import AddressParseError
from bs4 import BeautifulSoup
from rich import print



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



def find_code_in_html(next_row:BeautifulSoup) -> str:
    cells = next_row.select("td.RenderCell.Phase3")

    values = {}          

    for td in cells:
        h5 = td.find("h5")                 
        if not h5:

            continue                     

        heading = h5.get_text(strip=True)  

        narrative = " ".join(td.stripped_strings)

        narrative = narrative.replace(heading, "", 1).strip()

        values[heading] = narrative

    return values


def parse_zone_policies(response_text: str) -> dict:
    """Parse the zone policies from the response text."""
    soup= BeautifulSoup(response_text, 'html.parser')
    site_row = soup.find(
        lambda tag: tag.name == "tr" and "Site coverage" in tag.get_text(strip=True)
    )

    # 2️⃣  Step to the previous sibling <tr>
    next_row = site_row.find_next("tr")

    site_coverage = find_code_in_html(next_row)
    print(f"Site coverage: {site_coverage}")
    building_height = soup.find(
        lambda tag: tag.name == "tr" and "Building Height" in tag.get_text(strip=True)
    )
    next_row = building_height.find_next("tr")
    building_height = find_code_in_html(next_row)
    print(f"Building height: {building_height}")

    primary_street_setback= soup.find(
        lambda tag: tag.name == "tr" and "Primary Street Setback" in tag.get_text(strip=True)   
    )
    next_row = primary_street_setback.find_next("tr")
    primary_street_setback = find_code_in_html(next_row)
    print(f"Primary Street Setback: {primary_street_setback}")
    secondary_street_setback = soup.find(
        lambda tag: tag.name == "tr" and "Secondary Street Setback" in tag.get_text(strip=True)
    )
    next_row = secondary_street_setback.find_next("tr")
    secondary_street_setback = find_code_in_html(next_row)
    print(f"Secondary Street Setback: {secondary_street_setback}")
    appearance = soup.find(
        lambda tag: tag.name == "tr" and "Appearance" in tag.get_text(strip=True)
    )
    next_row = appearance.find_next("tr")
    appearance = find_code_in_html(next_row)
    print(f"Appearance: {appearance}")
    ancillary_buildings_and_structures=soup.find(
        lambda tag: tag.name == "tr" and "Ancillary buildings and structures" in tag.get_text(strip=True)   
    )
    next_row = ancillary_buildings_and_structures.find_next("tr")
    ancillary_buildings_and_structures = find_code_in_html(next_row)
    print(f"Ancillary Buildings and Structures: {ancillary_buildings_and_structures}")
    land_use_and_intensity= soup.find(
        lambda tag: tag.name == "tr" and "Land Use and Intensity" in tag.get_text(strip=True)   
    )
    next_row = land_use_and_intensity.find_next("tr")
    land_use_and_intensity = find_code_in_html(next_row)
    print(f"Land Use and Intensity: {land_use_and_intensity}")
    ancillary_buildings_and_structures= soup.find(
        lambda tag: tag.name == "tr" and "Ancillary buildings and structures" in tag.get_text(strip=True)   
    )





