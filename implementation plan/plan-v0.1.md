# bentoapp Implementation Plan (v0.1)
Date: 2025-Nov-30

## Objectives
- Deliver a Streamlit-like Python DX for data apps while running on production-grade FastAPI + HTMX + Alpine.
- Enforce extreme decomposition and validation (per Guideline-Methodology.pdf): small, well-tested units with red-flagging/guards to prevent bad states.
- Prioritize speed: async stack, minimal JS, Polars for data, cached static assets, orjson/gzip/brotli by default.

## Principles from Methodology
- **Maximal decomposition:** isolate app factory, routing, UI primitives, data adapters, perf middleware; each with clear contracts.
- **Error correction / red-flagging:** strict input/output validation, HTMX endpoint guards, template/type checks, fast fail paths.
- **Perf-first defaults:** uvloop + orjson, HTTP caching + compression, precompiled templates, minimal client payloads.
- **DX empathy:** Streamlit-like helpers (`@page`, `ui.metric/table/chart/form/grid`) with sensible defaults and examples.

## Phases and Exit Criteria
1) Foundation & DX design  
   - Finalize API surface (`page` decorator, `ui` primitives, data adapters), routing model, and component contracts.  
   - Define perf SLOs (TTFB, p95 render), validation rules, and telemetry hooks.  
   - Exit: reviewed design doc + interface stubs.

2) Scaffold package & CLI  
   - Create pyproject, `src/bentoapp/` skeleton (app factory, ui helpers, components, templates, static), Typer CLI (`new`, `dev`, `build-css`).  
   - Add tests harness (pytest + httpx), example project stub, and prebuilt CSS bundle.  
   - Exit: `pip install -e .` works; `bentoapp dev` runs sample app; lint/test green.

3) Components & data flows  
   - Implement bento grid utilities, cards (metric/stat/sparkline), table (Polars-backed pagination/filter via HTMX), chart block (fast JSON spec), forms/upload flow.  
   - Wire HTMX partial endpoints + Alpine glue; add validation/red-flagging on inputs/outputs.  
   - Exit: demo pages render and interactions work (filters, uploads, charts).

4) Performance & reliability  
   - Enable uvloop/orjson, compression, cache headers, template precompile; add caching helper (in-memory, Redis-ready).  
   - Add security headers, CSRF/HTMX guards, and error-handling patterns.  
   - Tests for perf/regression (smoke + HTML snapshots; micro-bench where feasible).  
   - Exit: perf baseline met, tests pass with guards enabled.

5) Docs & release prep  
   - Write README/guide with quickstart, recipes, deploy notes; document CLI.  
   - Version 0.0.1, publish checklist (PyPI), changelog start.  
   - Exit: release candidate tagged; docs ready for users.

## Tracking
- Phase status tracked in `project_phases.json` at repo root; update before advancing phases.
