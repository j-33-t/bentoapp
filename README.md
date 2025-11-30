# bentoapp

Streamlit-like Python DX on FastAPI + HTMX + Alpine with bento layouts, Polars-friendly data helpers, and HTMX tables/forms.

## Quickstart
```bash
pip install -e .
python -m bentoapp.cli demo
# or
bentoapp demo
```

Then open http://127.0.0.1:8000/demo

## Structure
- `src/bentoapp/`: app factory, UI primitives, CLI, templates, static CSS.
- `src/bentoapp/table.py`: table registry + renderer used by `/_bento/table/{id}` HTMX endpoint.
- `src/bentoapp/examples/demo/`: sample page using `@page_route`, `ui` helpers, table fragment, and HTMX forms/uploads.
- `tests/`: minimal smoke test.

## Features (current)
- FastAPI factory with HTMX/Alpine wired base template.
- UI helpers: page, grid, metric, text, form, input, upload, button.
- Table fragment with Polars support, HTMX pagination/sort via `/_bento/table/{id}`.
- CLI: `bentoapp demo`, `bentoapp dev`, `bentoapp new <name>`, `bentoapp build-css`.

## Next steps
- Add charts, validation guards, caching hooks, and more recipes.
