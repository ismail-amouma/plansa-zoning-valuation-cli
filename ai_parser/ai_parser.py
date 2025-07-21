from __future__ import annotations
from typing import Dict, Any
from scrapegraphai.graphs import SmartScraperGraph
from scrapegraphai.utils import prettify_exec_info
import inspect
from rich import print
from .graph_config import GRAPH_CONFIG
from .output_class import PlanningQuantitativeAssessment
from .system_prompt import DEFAULT_SIMPLE_PROMPT
import asyncio




async def scrape_zone_data(html: str, prompt: str = DEFAULT_SIMPLE_PROMPT) -> Dict[str, Any]:
    scraper = SmartScraperGraph(prompt=prompt, source=html, config=GRAPH_CONFIG,schema=PlanningQuantitativeAssessment)
    try:
        if inspect.iscoroutinefunction(scraper.run):
            raw = await scraper.run()
        else:
            raw = await asyncio.get_running_loop().run_in_executor(None, scraper.run)
        if GRAPH_CONFIG.get("verbose"):
            try:
                print("\n" + prettify_exec_info(scraper.get_execution_info()))
            except Exception:
                pass
        if not isinstance(raw, dict):
            raise ValueError("Scraper returned non-dict")
        print("Scraped data: %s", raw)
        return raw
    except Exception as e:
        raise ValueError(f"Scraping error: {e}") from e



