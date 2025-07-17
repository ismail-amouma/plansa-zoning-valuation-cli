from curl_cffi.requests import AsyncSession
from rich import print
import json
from bs4 import BeautifulSoup

async def get_tnv_raw(session: AsyncSession, valuation_sid: str) -> json:
    
    params = {
        'term': str(valuation_sid),
        'type': 'valuation',
        'filter':'full'
    }

    response = await session.get(

                        url='https://code.plan.sa.gov.au/int/_getzones',
                        params=params, 
                        impersonate='chrome'
                                )
    
    if response.status_code != 200:
        raise ValueError(f"Error fetching valuation data: {response.status_code} - {response.text}")
    if 'status' in response.json() :
        raise ValueError(f"Error fetching valuation data: {response.json()['status']} - {response.json().get('message', '')}")
    return response.json()


async def get_zone_policies_doc_id(session: AsyncSession, valuation_sid: str) -> str:
    
    params = {
        'term': str(valuation_sid),
        'type': 'valuation',
    }

    response = await session.get(

                        url='https://code.plan.sa.gov.au/int/_getpolicies',
                        params=params, 
                        impersonate='chrome'
                                )
    
    if response.status_code != 200:
        raise ValueError(f"Error fetching zone policies: {response.status_code} - {response.text}")
    if 'status' in response.json() :
        raise ValueError(f"Error fetching zone policies: {response.json()['status']} - {response.json().get('message', '')}")
    doc_ids = []
    for policy in response.json():
        if "Zone" in policy.get('DocTreeText') :
            if policy.get('HasChildren') is True:
                for child in policy.get('Children', []):
                        doc_ids.append(child.get('DocTreeID'))
    print(f"Zone Policies Doc IDs: {doc_ids}")
    return doc_ids



async def get_zone_policies_raw(session: AsyncSession, valuation_sid: str) -> list[list[dict]]:
    """Fetch zone policies for a given valuation SID."""
    doc_ids = await get_zone_policies_doc_id(session, valuation_sid)
    if not doc_ids:
        return []

    params = {
        'term': str(valuation_sid),
        'type': 'valuation',
        'filter': 'full'
    }
    policies_responses = []
    for doc_id in doc_ids:
        response = await session.get(
            url='https://code.plan.sa.gov.au/int/_getpolicies',
            params={**params, 'docId': doc_id},
            impersonate='chrome'
        )

        if response.status_code != 200:
            raise ValueError(f"Error fetching policy document {doc_id}: {response.status_code} - {response.text}")
        if 'status' in response.json():
            raise ValueError(f"Error fetching policy document {doc_id}: {response.json()['status']} - {response.json().get('message', '')}")
        response_json = response.json()
        if isinstance(response_json, list):
            policies_responses.append(response_json)
            content=response.json()[0].get('Content', '')
            soup= BeautifulSoup(content, 'html.parser')
            with open('exports/Zone Planning and Development Policies.html', 'w', encoding='utf-8') as file:
                file.write(soup.prettify())

    return policies_responses




