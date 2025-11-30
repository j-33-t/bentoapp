"""
Data helpers for table-friendly structures.
"""
from __future__ import annotations

from typing import Iterable, Optional, Sequence

import polars as pl


def to_table(
    data: pl.DataFrame | pl.LazyFrame | Iterable[dict],
    columns: Optional[Sequence[str]] = None,
) -> pl.DataFrame:
    if isinstance(data, pl.LazyFrame):
        df = data.collect()
    elif isinstance(data, pl.DataFrame):
        df = data
    else:
        df = pl.DataFrame(data)
    if columns:
        df = df.select(list(columns))
    return df
