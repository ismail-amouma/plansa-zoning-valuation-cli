# PlanSA Zoning Valuation CLI

This project solves a practical planning workflow problem in South Australia. Getting usable zoning rules for a property is usually manual, slow, and repetitive. This CLI takes an address or coordinates, resolves the valuation number, fetches the relevant PlanSA policy content, and converts the result into structured data that is easier to review and reuse.

## Problem it solves

Without tooling, the process usually means jumping between different services, copying policy text by hand, and manually reshaping that content into something consistent. With this CLI, the same flow runs in one command and returns valuation lookup, policy retrieval, and structured output in a single run.

## What it does

The tool accepts property input either as an address or as coordinates. It resolves the valuation ID from SA geospatial services, fetches zone policy HTML from PlanSA endpoints, parses quantitative controls into a typed Pydantic model called `PlanningQuantitativeAssessment`, and prints a clean structured result in the terminal.

## Why this project is valuable

The code handles real external integrations with government planning and geospatial services, uses an async Python workflow across multiple network calls, and deals with messy source formats like JSONP, nested payloads, and policy HTML. It also uses schema-constrained LLM extraction instead of free-form output, which keeps results more predictable for downstream use.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configure LLM credentials

On first run, the CLI prompts for credentials and saves them to `.env`. You can also set environment values manually. For OpenAI, set `LLM_PROVIDER=openai` and `OPENAI_API_KEY=...`. For Azure OpenAI, set `LLM_PROVIDER=azure`, `AZURE_API_KEY=...`, `AZURE_ENDPOINT=...`, and `AZURE_API_VERSION=...`.

## How to use

Run with an address:

```bash
python main.py --address "19 PALMER ST PROSPECT SA 5082"
```

Run with coordinates:

```bash
python main.py --coords -34.88994984664242 138.58712214002236
```

During execution, the CLI shows the resolved valuation SID, a policy preview, and the parsed quantitative assessment object.

## Output model (core fields)

The parser writes into `PlanningQuantitativeAssessment` in `ai_parser/output_class.py`. Core fields include `site_coverage`, `building_height_levels`, `building_height_m`, `primary_street_setback_m`, `secondary_street_setback`, and `car_parking_spaces`. Numeric constraints are represented by `NumericLimit`, which stores the direction (`min` or `max`), value, and unit.

## Project layout

The entry point and orchestration live in `main.py`. Address and coordinate lookup logic lives in `search/`, and zone policy retrieval lives in `valuation/`. The `ai_parser/` package contains prompt configuration, schema definitions, and parser graph setup. Typed lookup models are in `models.py`, helper parsing utilities are in `parsers.py`, sample artifacts are in `exports/`, and experimental scripts are in `scratch/`.

## Technical deep dive

Detailed scope and architecture are documented in `docs/PROJECT_SCOPE.md`.
