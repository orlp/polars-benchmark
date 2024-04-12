from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any

import modin.pandas as pd

from queries.common_utils import (
    check_query_result_pd,
    on_second_call,
    run_query_generic,
)
from settings import Settings

if TYPE_CHECKING:
    from collections.abc import Callable

settings = Settings()

pd.options.mode.copy_on_write = True

os.environ["MODIN_MEMORY"] = str(settings.run.modin_memory)


def _read_ds(table_name: str) -> pd.DataFrame:
    path = settings.dataset_base_dir / f"{table_name}.{settings.run.file_type}"

    if settings.run.file_type == "parquet":
        return pd.read_parquet(path, dtype_backend="pyarrow")
    elif settings.run.file_type == "csv":
        df = pd.read_csv(path, dtype_backend="pyarrow")
        for c in df.columns:
            if c.endswith("date"):
                df[c] = df[c].astype("date32[day][pyarrow]")
        return df
    elif settings.run.file_type == "feather":
        return pd.read_feather(path, dtype_backend="pyarrow")
    else:
        msg = f"unsupported file type: {settings.run.file_type!r}"
        raise ValueError(msg)


@on_second_call
def get_line_item_ds() -> pd.DataFrame:
    return _read_ds("lineitem")


@on_second_call
def get_orders_ds() -> pd.DataFrame:
    return _read_ds("orders")


@on_second_call
def get_customer_ds() -> pd.DataFrame:
    return _read_ds("customer")


@on_second_call
def get_region_ds() -> pd.DataFrame:
    return _read_ds("region")


@on_second_call
def get_nation_ds() -> pd.DataFrame:
    return _read_ds("nation")


@on_second_call
def get_supplier_ds() -> pd.DataFrame:
    return _read_ds("supplier")


@on_second_call
def get_part_ds() -> pd.DataFrame:
    return _read_ds("part")


@on_second_call
def get_part_supp_ds() -> pd.DataFrame:
    return _read_ds("partsupp")


def run_query(query_number: int, query: Callable[..., Any]) -> None:
    run_query_generic(
        query,
        query_number,
        "modin",
        query_checker=lambda df, q: check_query_result_pd(df._to_pandas(), q),
    )
