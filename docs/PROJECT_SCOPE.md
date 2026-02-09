# Project Scope: PlanSA Zoning Valuation CLI

## Project Definition

`PlanSA Zoning Valuation CLI` is a Python command-line workflow that connects property lookup services and PlanSA policy endpoints, then uses an LLM pipeline to convert raw zoning HTML into structured planning controls.

This is primarily an automation utility for planning/valuation analysis workflows, not yet a web app or API server.

## Primary Use Cases

- Quickly assess zoning controls for a property from an address.
- Run the same analysis from map coordinates.
- Convert semi-structured policy HTML into typed data for downstream comparison, reporting, or data pipelines.

## Non-Goals (Current State)

- No persistent storage/database integration.
- No formal HTTP API around this logic.
- No built-in report generation/export command.
- No packaged/released CLI binary.

## Runtime Pipeline In Detail

1. Startup and credentials
   - `main.py` calls `ensure_llm_credentials()`.
   - If `LLM_PROVIDER` is unset, user is prompted and `.env` is updated.
2. Input ingestion
   - CLI enforces exactly one of:
     - `--address`
     - `--coords LAT LON`
3. Valuation resolution
   - Address flow:
     - `search/address_search.py`
     - endpoint: `https://lsa1.geohub.sa.gov.au/.../findAddressCandidates`
   - Coordinate flow:
     - `search/coordinate_search.py`
     - endpoint: `https://lsa2.geohub.sa.gov.au/.../identify`
4. Policy retrieval
   - `valuation/valuation.py`:
     - fetches candidate doc IDs from `/_getpolicies`
     - fetches full policy documents by `docId`
5. LLM extraction
   - `ai_parser/ai_parser.py` runs `SmartScraperGraph`.
   - Prompt comes from `ai_parser/system_prompt.py`.
   - Output schema is `PlanningQuantitativeAssessment` in `ai_parser/output_class.py`.
6. Terminal output
   - Valuation SID, policy preview, and parsed structured result are printed.

## Modules And Responsibilities

- `main.py`
  - Orchestrates the end-to-end flow.
  - Handles CLI args and provider bootstrap.
- `settings.py`
  - Builds `LLM_CONFIG` based on `.env`.
- `search/address_search.py`
  - Address lookup and JSONP parsing.
  - Raises typed address errors from `search/address_search_erros.py`.
- `search/coordinate_search.py`
  - Coordinate conversion (EPSG:4326 -> EPSG:3857) and valuation lookup.
- `valuation/valuation.py`
  - Fetches zoning policy documents from PlanSA.
- `ai_parser/*`
  - Prompt definition, schema contract, and scraper execution.
- `parsers.py`
  - Helper utilities and legacy parsing logic.
- `scratch/*`
  - Experimental scripts only.

## External Integrations

- SA GeoHub (address and coordinate resolution)
  - `lsa1.geohub.sa.gov.au`
  - `lsa2.geohub.sa.gov.au`
- PlanSA code services
  - `code.plan.sa.gov.au`
- LLM provider
  - OpenAI or Azure OpenAI via ScrapeGraphAI

## Inputs And Outputs

- Inputs:
  - Property address string or `LAT LON`.
  - `.env` credentials for selected LLM provider.
- Outputs:
  - In-memory parsed object (printed to stdout).
  - Optional local artifacts in `exports/` from scratch scripts.

## Configuration

- Required base setting:
  - `LLM_PROVIDER` in `.env` (`openai` or `azure`)
- Provider-specific:
  - OpenAI: `OPENAI_API_KEY`
  - Azure: `AZURE_API_KEY`, `AZURE_ENDPOINT`, `AZURE_API_VERSION`

## Operational Notes

- The CLI currently performs live network calls for every run.
- There is minimal retry/backoff logic.
- Error handling is strongest in address lookup and less standardized in other modules.
- Some prototype files are mixed into repo (`scratch/`), so consumers should treat `main.py` as the production entrypoint.

## Current Risks And Gaps

- Limited automated tests.
- Some utilities are partial/legacy (`parsers.py`).
- Dependency declarations may need periodic review as integrations evolve.
- Secrets must never be committed in scripts or config files.

## How To Run

```bash
python main.py --address "19 PALMER ST PROSPECT SA 5082"
```

```bash
python main.py --coords -34.88994984664242 138.58712214002236
```

## Recommended Next Improvements

1. Add tests for:
   - address lookup
   - coordinate lookup
   - policy fetch fallback paths
2. Add output export options:
   - `--output-json`
   - `--output-csv`
3. Add logging levels and standardized exception classes across modules.
4. Split prototypes from runtime package and add CI checks.
