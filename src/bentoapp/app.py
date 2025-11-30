"""
FastAPI application factory with HTMX-friendly defaults.
"""
import inspect
from pathlib import Path
from typing import Awaitable, Callable, Iterable, Optional, Union

from fastapi import FastAPI, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .ui import Fragment, PageRegistry, render_fragment
from .table import table_registry, render_table_html

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


def create_app(
    *,
    pages: Optional[Iterable[Callable]] = None,
    title: str = "bentoapp",
) -> FastAPI:
    app = FastAPI(title=title, default_response_class=HTMLResponse)

    # Compression for faster payloads
    app.add_middleware(GZipMiddleware, minimum_size=512)

    @app.middleware("http")
    async def _security_headers(request: Request, call_next):
        response = await call_next(request)
        # Conservative defaults; static caching handled by StaticFiles
        response.headers.setdefault("Cache-Control", "no-store")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        return response

    # Static files (prebuilt CSS, htmx, alpine)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    templates = Jinja2Templates(directory=TEMPLATES_DIR)

    registry = PageRegistry()
    if pages:
        for page_fn in pages:
            path = getattr(page_fn, "__bento_path__", "/")
            methods = getattr(page_fn, "__bento_methods__", ["GET"])
            registry.register(page_fn, path=path, methods=methods)

    async def _call_fragment(fn: Callable, request: Request) -> Fragment:
        result = fn(request)
        if inspect.isawaitable(result):
            result = await result  # type: ignore[assignment]
        if isinstance(result, Fragment):
            return result
        return Fragment(str(result))

    # Register routes from pages
    for route in registry.routes():
        async def endpoint(request: Request, _fn=route.endpoint):
            fragment = await _call_fragment(_fn, request)
            return templates.TemplateResponse(
                "base.html",
                {
                    "request": request,
                    "title": title,
                    "body": render_fragment(fragment),
                },
            )

        app.add_api_route(
            route.path,
            endpoint,
            methods=route.methods,
            response_class=HTMLResponse,
            name=route.name,
        )

    @app.get("/_bento/table/{table_id}", response_class=HTMLResponse)
    async def _table_endpoint(table_id: str, request: Request, page: int = 1, page_size: int = 20, sort: Optional[str] = None, direction: str = "asc"):
        df = table_registry.dataframe_for(table_id)
        html = render_table_html(df, table_id=table_id, page=page, page_size=page_size, sort=sort, direction=direction)
        return HTMLResponse(html)

    @app.get("/", response_class=HTMLResponse)
    async def _root(request: Request):
        return templates.TemplateResponse(
            "base.html",
            {
                "request": request,
                "title": title,
                "body": render_fragment(registry.default_page_fragment()),
            },
        )

    return app
