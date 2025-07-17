from valuation.valuation import get_tnv_raw, get_zone_policies_raw
from search.address_search import get_address
import json
from rich import print





def main():
    import asyncio
    from curl_cffi.requests import AsyncSession

    async def run():
        async with AsyncSession() as session:
            address_response= await get_address(session, "9 ELIZABETH ST NORWOOD SA 5067")
            valuation_sid = json.loads(address_response.model_dump_json()).get('Valuation', {})
            print(f"Valuation SID: {valuation_sid} from address :{address_response.full_address}")
            try:
                tnv_data = await get_tnv_raw(session, valuation_sid)
                with open('exports/tnv_data.json', 'w', encoding='utf-8') as f:
                    json.dump(tnv_data, f, indent=4)
                print("TNV data saved to tnv_data.json")
                print("Sample TNV data:", json.dumps(tnv_data[:1], indent=4) if isinstance(tnv_data, list) else str(tnv_data)[:500])

                zone_policies = await get_zone_policies_raw(session, valuation_sid)
                with open('exports/zone_policies.json', 'w', encoding='utf-8') as f:
                  json.dump(zone_policies, f, indent=4)
                print("Zone policies response saved to zone_policies.json")
                print("Sample zone policies Table full response:", json.dumps(zone_policies[:1], indent=4) if isinstance(zone_policies, list) else str(zone_policies)[:500])

            except Exception as e:
                print(f"An error occurred: {e}")

    asyncio.run(run())



if __name__ == "__main__":
    """This is just the scraping with no parsing , Still need to implement the parsing logic"""
    main()