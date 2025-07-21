from curl_cffi import requests
from rich import print
import json
from pyproj import Transformer

# build once, then reuse
to_3857 = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
to_4326 = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

lon, lat =   138.58712214002236 ,-34.88994984664242       # Google Maps pair
print(f"Google Maps pair: {lon}, {lat}")
x, y = to_3857.transform(lon, lat)   
print(f"Web Mercator pair: {x}, {y}")
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
print(f"Request Params: {params}")
response = requests.get(
    'https://lsa2.geohub.sa.gov.au/arcgis/rest/services/SAPPA/PropertyPlanningAtlasV16/MapServer/identify',
    params=params,
    impersonate='chrome'
)



print(response.status_code)
print(response.json())
with open('exports/identify_response.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, indent=4)

"""
UP LEFT :12031445.498769322,-3049697.596389441,16710614.622273428,-860541.106302574
UP RIGHT :13227532.117375445,-3074157.445440691,17906701.24087955,-885000.9553538242
DOWN LEFT :12875310.291037444,-5605751.822245056,17554479.41454155,-3416595.3321581893
DOWN RIGHT :13227532.117375445,-3074157.445440691,17906701.24087955,-885000.9553538242
"""