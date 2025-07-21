import argparse
import asyncio
import json
import os
from pathlib import Path
from typing import Tuple

from dotenv import load_dotenv, set_key
from curl_cffi.requests import AsyncSession
from rich import print
from rich.prompt import Prompt

from valuation.valuation import get_zone_policies_raw
from search.address_search import get_address
from search.coordinate_search import get_address as get_address_from_coordinates


# Path to .env file
ENV_PATH = Path(".env")


def ensure_llm_credentials():
    """Ensure LLM credentials are set in the environment, otherwise prompt and save."""
    load_dotenv(ENV_PATH)

    provider = os.getenv("LLM_PROVIDER")
    if provider:
        print(f"[green]LLM Provider already set to:[/green] {provider}")
        return

    print("[bold yellow]No LLM credentials found. Let's configure them.[/bold yellow]")
    provider_choice = Prompt.ask("Choose your LLM provider", choices=["openai", "azure"], default="openai")

    if provider_choice == "openai":
        api_key = Prompt.ask("[bold cyan]Enter your OpenAI API Key[/bold cyan]")
        set_key(ENV_PATH, "LLM_PROVIDER", "openai")
        set_key(ENV_PATH, "OPENAI_API_KEY", api_key)
        print("[green]OpenAI credentials saved to .env[/green]")

    elif provider_choice == "azure":
        api_key = Prompt.ask("[bold cyan]Enter your Azure OpenAI API Key[/bold cyan]")
        endpoint = Prompt.ask("[bold cyan]Enter your Azure Endpoint URL[/bold cyan]")
        api_version = Prompt.ask("[bold cyan]Enter your Azure API Version[/bold cyan]")

        set_key(ENV_PATH, "LLM_PROVIDER", "azure")
        set_key(ENV_PATH, "AZURE_API_KEY", api_key)
        set_key(ENV_PATH, "AZURE_ENDPOINT", endpoint)
        set_key(ENV_PATH, "AZURE_API_VERSION", api_version)

        print("[green]Azure OpenAI credentials saved to .env[/green]")


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
    ensure_llm_credentials()

    args = cli()
    from ai_parser.ai_parser import scrape_zone_data

    async with AsyncSession() as session:
        try:
            if args.address:
                valuation_sid = await fetch_by_address(session, args.address)
            else:
                lat, lon = args.coords
                valuation_sid = await fetch_by_coordinates(session, (lat, lon))

            zone_policies = await get_zone_policies_raw(session, valuation_sid)
            html = zone_policies[0][0].get('Content', '') if zone_policies else ''
            print(f"[bold]Zone Policies Preview:[/bold] {html[:500]} ...")

            print("[yellow]Parsing zoning data using AI...[/yellow]")
            parsed_data = await scrape_zone_data(html)
            print(f"[green]Parsed Zone Data:[/green]\n{parsed_data}")

        except Exception as e:
            print(f"[red]An error occurred:[/red] {e}")


if __name__ == "__main__":
    asyncio.run(main())
