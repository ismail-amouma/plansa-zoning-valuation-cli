import argparse
import asyncio
import json
from typing import Tuple

from curl_cffi.requests import AsyncSession
from valuation.valuation import get_zone_policies_raw
from search.address_search import get_address
from search.coordinate_search import get_address as get_address_from_coordinates
from ai_parser.ai_parser import scrape_zone_data
from rich import print


def cli():
    parser = argparse.ArgumentParser(description="Zoning Valuation CLI")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--address', type=str, help='Property address (e.g., "9 ELIZABETH ST NORWOOD SA 5067")')
    group.add_argument('--coords', nargs=2, type=float, metavar=('LAT', 'LON'),
                       help='Latitude and Longitude coordinates')
    return parser.parse_args()


async def fetch_by_address(session: AsyncSession, address: str):
    address_response = await get_address(session, address)
    valuation_sid = json.loads(address_response.model_dump_json()).get('Valuation', {})
    print(f"[bold green]Valuation SID:[/bold green] {valuation_sid} from address: [cyan]{address_response.full_address}[/cyan]")
    return valuation_sid


async def fetch_by_coordinates(session: AsyncSession, coords: Tuple[float, float]):
    address_response = await get_address_from_coordinates(session, coords)
    valuation_sid = address_response.attributes.Valuation_No
    print(f"[bold green]Valuation SID:[/bold green] {valuation_sid} from coordinates: [cyan]{coords}[/cyan]")
    return valuation_sid


async def main():
    args = cli()
    async with AsyncSession() as session:
        try:
            if args.address:
                valuation_sid = await fetch_by_address(session, args.address)
            else:
                lat, lon = args.coords
                valuation_sid = await fetch_by_coordinates(session, (lat, lon))

            zone_policies = await get_zone_policies_raw(session, valuation_sid)
            print(f"[bold]Zone Policies Preview:[/bold] {zone_policies[0][0].get('Content', '')[:500]} ...")

            html = zone_policies[0][0].get('Content', '')
            print("[yellow]Parsing zoning data using AI...[/yellow]")
            parsed_data = await scrape_zone_data(html)
            print(f"[green]Parsed Zone Data:[/green] {parsed_data}")

        except Exception as e:
            print(f"[red]An error occurred:[/red] {e}")


if __name__ == "__main__":
    asyncio.run(main())
