from __future__ import annotations
from curl_cffi.requests import AsyncSession
from models import Coordinate_Search, Attribute
from typing import Tuple
from pyproj import Transformer



to_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
to_4326 = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)



async def get_address(session: AsyncSession, coordinate:Tuple) -> Coordinate_Search:
    """Fetch address details from the remote geocoder using coordinates.

    Returns a Coordinate_Search object with address details.
    """

    lat,lon = coordinate
    x, y = to_3857.transform(lon, lat)
    params = {
      'f': 'json',
      'tolerance': '0',
      'returnGeometry': 'false',
      'returnFieldName': 'false',
      'returnUnformattedValues': 'false',
      'imageDisplay': '1913,233,96',
      'geometry': f'{{"x":{x},"y":{y}}}',
      'geometryType': 'esriGeometryPoint',
      'sr': '3857',
      'mapExtent': '12031445.498769322, -5605751.822245056, 17906701.24087955, -860541.106302574',
      'layers': 'all:43',
    }
    response =await session.get(
          'https://lsa2.geohub.sa.gov.au/arcgis/rest/services/SAPPA/PropertyPlanningAtlasV16/MapServer/identify',
          params=params,
          impersonate='chrome'
      )
    
    if response.status_code != 200:
        raise ValueError(f"Error fetching address data: {response.status_code} - {response.text}")
    response_json = response.json()
    result = response_json.get('results', [])
    if len(result) == 0:
        raise ValueError(f"No address found for coordinates: {coordinate}")
    print(result[0])
    return Coordinate_Search(
        layerId= result[0]['layerId'],
        layerName=result[0]['layerName'],
        displayFieldName=result[0]['displayFieldName'],
        value=result[0]['value'],
        attributes=Attribute(
            Location=result[0]['attributes']['Location'],
            OBJECTID=result[0]['attributes']['OBJECTID'],
            Shape=result[0]['attributes']['Shape'],
            Valuation_No=result[0]['attributes']['Valuation No'],
            Title_Prefix=result[0]['attributes']['Title Prefix'],
            Title_Volume=result[0]['attributes']['Title Volume'],
            Title_Folio=result[0]['attributes']['Title Folio']
        )
    )






