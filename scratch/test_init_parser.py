import argparse
import json
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
from bs4 import BeautifulSoup



CRITERIA = [
    "Land Use",
    "Site Coverage",
    "Building Height",
    "Wall Height",
    "Primary Street Setback",
    "Secondary Street Setback",
    "Lower Side Setbacks",
    "Upper Side Setbacks",
    "Lower Rear Setback",
    "Upper Rear Setback",
    "Earthworks",
    "Overlooking",
    "Tree Planting",
    "Streetscape",
    "Garage Setback",
    "Garage Opening",
    "Garage Crossover",
    "Private Open Space",
    "Soft Landscaping",
    "Car Parking",
]


_WS = re.compile(r"\s+")


def clean(text: str) -> str:
    return _WS.sub(" ", text).strip()


def mm_or_m_to_m(text: str) -> Optional[float]:
    """Return metres as float if a unit found; None otherwise."""
    if not text:
        return None
    s = text.lower()
    m = re.search(r"([\d.]+)\s*mm", s)
    if m:
        return float(m.group(1)) / 1000.0
    m = re.search(r"([\d.]+)\s*m\b", s)
    if m:
        return float(m.group(1))
    m = re.search(r"([\d.]+)", s)
    if m:
        return float(m.group(1))
    return None


def pct(text: str) -> Optional[float]:
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    return float(m.group(1)) if m else None



@dataclass
class TNVRecord:
    label: str
    values: Dict[str, str]  # dwelling type -> string value
    description: str
    raw_code: str


def parse_tnv_json(path: Path) -> Dict[str, TNVRecord]:
    """
    Parse the TNV json payload from SAPPA.
    Returns mapping keyed by lower-case label text (e.g. "minimum frontage").
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    recs: Dict[str, TNVRecord] = {}

    for item in data.get("List", []):
        if item.get("GroupType", "").lower().startswith("local variation"):
            desc_html = item.get("Description") or ""
            desc_txt = clean(BeautifulSoup(desc_html, "html.parser").get_text(" ", strip=True))
            # label before parenthesis
            label = desc_txt.split("(")[0].strip()
            raw_code = item.get("Code") or ""

            # Values encoded after "|" separated by underscores.
            # Example: V0004|_9_8_6_18_18  (detached, semi, row, group, flat)
            values: Dict[str, str] = {}
            after = raw_code.split("|", 1)[1] if "|" in raw_code else ""
            bits = [b for b in after.split("_") if b != ""]
            dwelling_keys = ["detached", "semi_detached", "row", "group", "flat"]
            for k, b in zip(dwelling_keys, bits):
                values[k] = b

            recs[label.lower()] = TNVRecord(
                label=label,
                values=values,
                description=desc_txt,
                raw_code=raw_code,
            )

    return recs


def parse_code_values_from_html(path: Path) -> Dict[str, str]:
    """
    Heuristic scrape: grabs plain-text from HTML and uses regex patterns
    to pull headline numeric/value strings relevant to each criterion.

    Returns dict {Criterion -> ValueString or None}.
    """
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    vals: Dict[str, Optional[str]] = {}

    # Land Use: if 'dwelling' appears at all we assume Dwelling (detached)
    if "dwelling" in text.lower():
        vals["Land Use"] = "Dwelling (detached)"
    else:
        vals["Land Use"] = None

    # Site Coverage
    m = re.search(r"(\d+(?:\.\d+)?)\s*%\s*site coverage", text, flags=re.I)
    vals["Site Coverage"] = f"Max. {m.group(1)}%" if m else None

    # Building Height: first try "Maximum building height is X levels"
    m_lvl = re.search(r"Maximum\s+building\s+height\s+is\s+(\d+)\s+level", text, flags=re.I)
    m_m = re.search(r"(\d+(?:\.\d+)?)\s*m\s+(?:high|height)", text, flags=re.I)
    if m_lvl and m_m:
        vals["Building Height"] = f"Max. {m_lvl.group(1)} levels/{m_m.group(1)}m"
    elif m_lvl:
        vals["Building Height"] = f"Max. {m_lvl.group(1)} levels"
    elif m_m:
        vals["Building Height"] = f"Max. {m_m.group(1)}m"
    else:
        vals["Building Height"] = None

    # Wall Height (often not explicit; fallback typical 7m if none)
    m = re.search(r"wall height[^.]*?(\d+(?:\.\d+)?)\s*m", text, flags=re.I)
    vals["Wall Height"] = f"Max. {m.group(1)}m" if m else "Max. 7m"  # conservative fallback

    # Primary Street Setback
    # We'll capture the common garage figure 5.5m; if not found, leave None.
    m = re.search(r"5\.5\s*m.*primary\s+street", text, flags=re.I)
    if m:
        vals["Primary Street Setback"] = "5.5m"
    else:
        # look for phrase with primary street and metres ahead
        m2 = re.search(r"primary\s+street[^0-9]*?(\d+(?:\.\d+)?)\s*m", text, flags=re.I)
        vals["Primary Street Setback"] = f"{m2.group(1)}m" if m2 else None

    # Secondary Street Setback
    # Pattern: (other than a rear laneway) ... no less than: <number> m or 900mm whichever
    m = re.search(r"secondary\s+street[^0-9]*?(\d+(?:\.\d+)?)\s*m", text, flags=re.I)
    if m:
        vals["Secondary Street Setback"] = f"{m.group(1)}m"
    else:
        # fallback to 900mm
        mm = re.search(r"secondary[^0-9]*?900\s*mm", text, flags=re.I)
        vals["Secondary Street Setback"] = "900mm" if mm else None

    # Lower/Upper Side Setbacks – use descriptive strings (rules/formula)
    vals["Lower Side Setbacks"] = "Boundary wall ≤3m high & 11.5m long; else 900mm"
    vals["Upper Side Setbacks"] = "900mm + 1/3 wall height above 3m"

    # Rear Setbacks (lower/upper)
    # Search for 'rear boundary' then numbers
    m4 = re.search(r"rear[^0-9]*?(\d+(?:\.\d+)?)\s*m", text, flags=re.I)
    vals["Lower Rear Setback"] = f"Min. {m4.group(1)}m" if m4 else "Min. 4m"
    # assume +2m upper
    vals["Upper Rear Setback"] = "Min. 6m"

    # Clause refs for remainder
    vals["Earthworks"] = "DTS 8.1"
    vals["Overlooking"] = "DTS 10.1"
    vals["Tree Planting"] = "DTS 13.1 (4x4m deep soil)"
    vals["Streetscape"] = "DTS 17.1"
    vals["Garage Setback"] = "DTS 20.1"
    vals["Garage Opening"] = "DTS 20.1"
    vals["Garage Crossover"] = "DTS 23.3"
    vals["Private Open Space"] = "DTS 21.1"
    vals["Soft Landscaping"] = "DTS 22.1"
    vals["Car Parking"] = "Min. 2 parking spaces"

    return vals



def build_rows(
    html_vals: Dict[str, str],
    tnv_map: Dict[str, TNVRecord],
    criteria: List[str] = CRITERIA,
) -> List[Dict[str, Any]]:
    """
    Assemble rows matching screenshot columns: Criteria, Value, TNV, Met.
    - Value from html_vals
    - TNV from tnv_map (only Building Height currently maps cleanly)
    - Met left None (you can fill after comparing design measurements)
    """
    rows: List[Dict[str, Any]] = []

    # helpful TNVs
    tnv_bldg = tnv_map.get("maximum building height (levels)")
    tnv_frontage = tnv_map.get("minimum frontage")
    tnv_sitearea = tnv_map.get("minimum site area")

    for crit in criteria:
        val = html_vals.get(crit)
        tnv = None

        if crit == "Building Height" and tnv_bldg:
            lvl = tnv_bldg.values.get("detached")
            if lvl:
                tnv = f"{lvl} level(s)"

        # (optional) attach other TNVs in notes if you want; for now None
        row = {
            "Criteria": crit,
            "Value": val,
            "TNV": tnv,
            "Met": None,    # you’ll set this later
        }
        rows.append(row)

    return rows


# ------------------------------------------------------------------
# Public top-level convenience
# ------------------------------------------------------------------
def parse_sappa_files(
    html_path: Path,
    tnv_path: Path,
    include_extra_tnvs: bool = False,
) -> Tuple[List[Dict[str, Any]], pd.DataFrame, Dict[str, TNVRecord]]:
    """
    Parse both files and return:
        rows        -> list of dicts (Criteria/Value/TNV/Met)
        df          -> pandas DataFrame of rows
        tnv_records -> full TNVRecord dict (if caller needs extra info)
    """
    html_vals = parse_code_values_from_html(Path(html_path))
    tnv_map = parse_tnv_json(Path(tnv_path))
    rows = build_rows(html_vals, tnv_map)
    df = pd.DataFrame(rows, columns=["Criteria", "Value", "TNV", "Met"])
    return rows, df, tnv_map

HTML_FILE = Path("exports/Zone Planning and Development Policies.html")
TNV_FILE = Path("exports/tnv_data.json")

rows, df, tnv_map = parse_sappa_files(HTML_FILE, TNV_FILE)

print(df)

