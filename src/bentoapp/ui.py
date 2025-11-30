"""
Server-rendered UI primitives and page registry.
This is a lightweight starting point; components render to HTML strings for HTMX swaps.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable, List, Optional, Sequence
from markupsafe import Markup, escape


# Simple fragment wrapper for safe HTML snippets.
@dataclass
class Fragment:
    html: str


def render_fragment(fragment: Fragment | str) -> Markup:
    if isinstance(fragment, Fragment):
        return Markup(fragment.html)
    return Markup(str(fragment))


def join(children: Iterable[Fragment | str]) -> Fragment:
    return Fragment("".join(str(render_fragment(c)) for c in children))


# Layout primitives
def page(title: str, *children: Fragment | str) -> Fragment:
    return Fragment(
        f"<div class='page'><header class='page__header'><h1>{escape(title)}</h1></header>"
        f"<main class='page__body'>{render_fragment(join(children))}</main></div>"
    )


def grid(children: Sequence[Fragment | str], min_col: int = 240, gap: str = "var(--space-4)") -> Fragment:
    return Fragment(
        f"<div class='bento-grid' style='--bento-min:{min_col}px;gap:{gap};'>"
        f"{render_fragment(join(children))}</div>"
    )


def metric(label: str, value: Any, delta: Optional[str] = None) -> Fragment:
    delta_html = (
        f"<span class='metric__delta' aria-label='delta'>{escape(delta)}</span>"
        if delta is not None
        else ""
    )
    return Fragment(
        "<div class='card metric'>"
        f"<div class='metric__label'>{escape(label)}</div>"
        f"<div class='metric__value'>{escape(value)}</div>"
        f"{delta_html}"
        "</div>"
    )


def text(body: str) -> Fragment:
    return Fragment(f"<p class='text'>{escape(body)}</p>")


def form(
    *children: Fragment | str,
    action: str,
    method: str = "post",
    hx: bool = True,
    target: Optional[str] = None,
    swap: str = "innerHTML",
) -> Fragment:
    hx_attrs = ""
    if hx:
        hx_attrs = f" hx-{escape(method)}='{escape(action)}'"
        if target:
            hx_attrs += f" hx-target='{escape(target)}'"
        hx_attrs += f" hx-swap='{escape(swap)}'"
    return Fragment(
        f"<form class='form' action='{escape(action)}' method='{escape(method)}'{hx_attrs}>"
        f"{render_fragment(join(children))}"
        "</form>"
    )


def input_text(name: str, label: str, placeholder: str = "", value: str = "") -> Fragment:
    return Fragment(
        "<label class='form__field'>"
        f"<span>{escape(label)}</span>"
        f"<input type='text' name='{escape(name)}' placeholder='{escape(placeholder)}' value='{escape(value)}' />"
        "</label>"
    )


def upload(name: str, label: str, accept: Optional[str] = None) -> Fragment:
    acc = f" accept='{escape(accept)}'" if accept else ""
    return Fragment(
        "<label class='form__field'>"
        f"<span>{escape(label)}</span>"
        f"<input type='file' name='{escape(name)}'{acc} />"
        "</label>"
    )


def button(label: str, kind: str = "primary") -> Fragment:
    return Fragment(f"<button class='btn btn--{escape(kind)}' type='submit'>{escape(label)}</button>")


# Page registration
RouteHandler = Callable[..., Awaitable[Fragment] | Fragment]


@dataclass
class Route:
    path: str
    methods: List[str]
    endpoint: RouteHandler
    name: str


class PageRegistry:
    def __init__(self) -> None:
        self._routes: List[Route] = []
        self._default: Optional[Route] = None

    def register(self, fn: RouteHandler, path: str = "/", methods: Sequence[str] | None = None) -> None:
        methods = list(methods or ["GET"])
        route = Route(path=path, methods=[m.upper() for m in methods], endpoint=fn, name=fn.__name__)
        self._routes.append(route)
        if path == "/" or self._default is None:
            self._default = route

    def routes(self) -> List[Route]:
        return list(self._routes)

    def default_page_fragment(self) -> Fragment:
        if self._routes:
            links = "".join(
                f"<li><a href='{escape(r.path)}'>{escape(r.name)} — {escape(r.path)}</a></li>"
                for r in self._routes
            )
            return Fragment(
                "<div class='card notice'>"
                "<div class='notice__title'>Bentoapp starter</div>"
                "<p>Select a page to view:</p>"
                f"<ul class='notice__list'>{links}</ul>"
                "</div>"
            )
        return Fragment("<div class='notice'>No pages registered.</div>")


# Decorator for pages
def page_route(path: str, methods: Sequence[str] | None = None) -> Callable[[RouteHandler], RouteHandler]:
    methods = list(methods or ["GET"])

    def decorator(fn: RouteHandler) -> RouteHandler:
        setattr(fn, "__bento_path__", path)
        setattr(fn, "__bento_methods__", methods)
        return fn

    return decorator
