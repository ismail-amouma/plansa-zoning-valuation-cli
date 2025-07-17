from __future__ import annotations
from curl_cffi.requests import AsyncSession

async def creat_session() -> AsyncSession:  
    """Create an asynchronous HTTP session."""
    return AsyncSession()

async def close_session(session: AsyncSession) -> None:
    """Close the asynchronous HTTP session."""
    await session.close()
