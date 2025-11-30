# bentoapp Foundation & DX Design (v0.1)
Date: 2024-Nov-30

## Goals
- Streamlit-like Python ergonomics for data apps; production-grade FastAPI + HTMX + Alpine under the hood.
- Blazing fast defaults: async everywhere, tiny payloads, cacheable static, minimal JS, Polars for data.
- Safety and correctness via small components, strict validation/red-flagging, and predictable routing.

## Non-goals (v0.1)
- No heavy JS build or component zoo; keep to HTMX/Alpine and prebuilt CSS.
- No complex auth/SSO in first drop (leave hooks); no task queue baked-in yet.

## Target users
- Data scientists/analysts comfortable in Python, minimal frontend.
- Engineers needing quick but production-safe data views.

## API surface (Python)
- `@page(path="/foo", methods=["get", "post"])` decorator registers a page function returning `ui.Fragment`.
- `ui` primitives (server-rendered, HTMX-capable):  
  - layout: `ui.page(title, children)`, `ui.grid(cols, gap, children)`, `ui.section(...)`, `ui.tabs(...)`.  
  - cards: `ui.metric(label, value, delta=None, icon=None)`, `ui.stat(label, body, foot=None)`.  
  - table: `ui.table(data, *, columns=None, sort=None, paginate=True, page_size=50, id=None)`; accepts Polars/LazyFrame/pandas/records; HTMX endpoints for filter/sort/paginate.  
  - chart: `ui.chart(id, spec, engine="echarts")` (fast JSON spec, client-rendered with minimal JS).  
  - form/upload: `ui.form(fields, action, method="post", hx=True)`, `ui.upload(...)` with server-side validation.  
  - text/html: `ui.text(...)`, `ui.code(...)`, `ui.badge(...)`, `ui.button(...)` with HTMX attrs.  
- Data helpers: `data.to_table(data, columns=None) -> TableModel`, `cache.get/set` helper for Polars outputs.
- HTMX helpers: `hx(endpoint, trigger="change", target="#id", swap="innerHTML")` for declarative bindings.

## Routing & rendering
- Central FastAPI app factory; routes auto-registered via decorator; HTMX endpoints for partials (table pages, filters, uploads).  
- Templates: Jinja base layout + partials for components; fragments rendered server-side; HTMX swaps update targets.  
- Static: shipped `static/` includes prebuilt CSS, htmx, alpine, tiny chart runtime (ECharts/Plotly lite).

## Layout & styling (bento-forward)
- CSS tokens in `:root` (`--surface-1/2`, `--accent`, `--space-*`, `--radius-*`, `--shadow-*`, `--font-*`).  
- Bento grid utility: `.bento-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(var(--bento-min, 240px),1fr)); gap:var(--space-4); }`.  
- Card variants: metric, chart, table, form; responsive single column on small, auto-fit on larger.

## Performance defaults
- FastAPI + uvicorn + uvloop; orjson responses; gzip/brotli via middleware; cache headers for static.  
- Template precompile at startup; minimal inline Alpine snippets; defer chart JS load.  
- Polars for data ops; optional lazy evaluation; avoid pandas unless user opts in.  
- Caching helper (in-memory by default, Redis-ready interface) for table pages and chart data.

## Validation & red-flagging
- Input/output validation via pydantic for endpoints; table/chart spec schemas; upload size/type guards.  
- HTMX guard middleware: reject missing `HX-Request` on partial endpoints; rate limit bursty endpoints (hook).  
- Error boundaries: component-level fallbacks; clear HTTP errors for invalid specs; logging with request ids.

## CLI (Typer) commands
- `bentoapp new <name>`: scaffold project with sample pages, tests, prebuilt CSS.  
- `bentoapp dev`: run uvicorn with reload.  
- `bentoapp build-css`: optional rebuild of CSS (ship prebuilt by default).  
- `bentoapp demo`: run example app.

## Project structure (scaffold target)
- `pyproject.toml` (fastapi, uvicorn[standard], jinja2, orjson, polars, httpx, typer, python-multipart).  
- `src/bentoapp/`: `app.py` (factory), `ui.py` (primitives), `components/`, `templates/`, `static/`, `cli.py`, `data.py`, `cache.py`, `htmx.py`.  
- `examples/`: dashboard + data explorer.  
- `tests/`: pytest + httpx client; HTML snapshots for components.

## Security & reliability
- Security headers middleware (CSP skeleton, no inline eval), HTTPS-ready.  
- CSRF token for form POSTs; double-submit for HTMX where relevant.  
- Upload sanitization (size/type), temp file handling.  
- Telemetry hooks: request timing, error logging, optional OpenTelemetry stub.

## Phase exits
- Exit Phase 1: this design reviewed; interfaces stable enough to scaffold.  
- Exit Phase 2: `pip install -e .`, `bentoapp dev` runs sample app, tests/lint pass.
