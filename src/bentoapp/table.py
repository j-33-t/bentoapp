"""
Table registry and rendering utilities for HTMX-driven tables.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional, Sequence

import polars as pl
from markupsafe import escape

from .data import to_table
from .ui import Fragment, render_fragment


TableProvider = Callable[[], pl.DataFrame]


@dataclass
class TableConfig:
    id: str
    provider: TableProvider | pl.DataFrame | Iterable[dict]
    columns: Optional[Sequence[str]] = None
    page_size: int = 20


class TableRegistry:
    def __init__(self) -> None:
        self._tables: Dict[str, TableConfig] = {}

    def register(self, config: TableConfig) -> None:
        self._tables[config.id] = config

    def get(self, table_id: str) -> TableConfig:
        if table_id not in self._tables:
            raise KeyError(f"Table '{table_id}' is not registered.")
        return self._tables[table_id]

    def dataframe_for(self, table_id: str) -> pl.DataFrame:
        cfg = self.get(table_id)
        provider = cfg.provider
        if callable(provider):
            df = provider()
        else:
            df = provider
        return to_table(df, columns=cfg.columns)


table_registry = TableRegistry()


def _paginated(df: pl.DataFrame, page: int, page_size: int, sort: Optional[str], direction: str) -> tuple[pl.DataFrame, int]:
    if sort and sort in df.columns:
        df = df.sort(sort, descending=direction.lower() == "desc")
    total_rows = df.height
    total_pages = max(1, math.ceil(total_rows / page_size)) if page_size else 1
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size if page_size else 0
    rows = df.slice(start, page_size) if page_size else df
    return rows, total_pages


def render_table_html(
    df: pl.DataFrame,
    table_id: str,
    page: int,
    page_size: int,
    sort: Optional[str] = None,
    direction: str = "asc",
) -> str:
    rows, total_pages = _paginated(df, page, page_size, sort, direction)
    cols = rows.columns
    next_dir = "desc" if direction == "asc" else "asc"
    header_cells = "".join(
        f"<th><button hx-get='/_bento/table/{escape(table_id)}?page=1&page_size={page_size}&sort={escape(col)}&direction={next_dir}' "
        f"hx-target='#table-{escape(table_id)}' hx-swap='outerHTML'>{escape(col)}</button></th>"
        for col in cols
    )
    body_rows = "".join(
        "<tr>" + "".join(f"<td>{escape(val)}</td>" for val in row) + "</tr>"
        for row in rows.iter_rows()
    )
    prev_page = max(1, page - 1)
    next_page = min(total_pages, page + 1)
    pager = (
        f"<div class='table__pager'>"
        f"<button hx-get='/_bento/table/{escape(table_id)}?page={prev_page}&page_size={page_size}&sort={escape(sort or '')}&direction={escape(direction)}' "
        f"hx-target='#table-{escape(table_id)}' hx-swap='outerHTML' {'disabled' if page<=1 else ''}>Prev</button>"
        f"<span>Page {page} / {total_pages}</span>"
        f"<button hx-get='/_bento/table/{escape(table_id)}?page={next_page}&page_size={page_size}&sort={escape(sort or '')}&direction={escape(direction)}' "
        f"hx-target='#table-{escape(table_id)}' hx-swap='outerHTML' {'disabled' if page>=total_pages else ''}>Next</button>"
        f"</div>"
    )
    return (
        f"<div class='card table-card' id='table-{escape(table_id)}'>"
        f"<div class='table__viewport'>"
        f"<table class='table'><thead><tr>{header_cells}</tr></thead><tbody>{body_rows}</tbody></table>"
        f"</div>"
        f"{pager}"
        f"</div>"
    )


def table_fragment(
    data: pl.DataFrame | pl.LazyFrame | Iterable[dict] | TableProvider,
    table_id: str,
    page_size: int = 20,
    columns: Optional[Sequence[str]] = None,
    sort: Optional[str] = None,
    direction: str = "asc",
) -> Fragment:
    cfg = TableConfig(id=table_id, provider=data, columns=columns, page_size=page_size)
    table_registry.register(cfg)
    df = table_registry.dataframe_for(table_id)
    html = render_table_html(df, table_id=table_id, page=1, page_size=page_size, sort=sort, direction=direction)
    return Fragment(html)
