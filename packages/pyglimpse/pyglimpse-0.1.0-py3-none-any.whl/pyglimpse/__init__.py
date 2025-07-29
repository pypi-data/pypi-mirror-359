import pandas as pd
import numpy as np
from pandas.api.types import (
    is_datetime64_any_dtype,
    is_string_dtype,
)

def _format_default_preview(series: pd.Series, max_n: int) -> str:
    values = series.head(max_n).to_list()
    values_str_list = []
    for v in values:
        if pd.isna(v):
            values_str_list.append("NA")
        elif isinstance(v, str):
            values_str_list.append(f'"{v}"')
        else:
            values_str_list.append(str(v))
    return ", ".join(values_str_list)

def glimpse(df: pd.DataFrame, width: int = 80, max_n: int = 10):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    rows, cols = df.shape
    print(f"Rows: {rows:,}")
    print(f"Columns: {cols:,}")
    print("-" * width)
    if df.empty:
        print("DataFrame is empty.")
        return
    DTYPE_MAP = {
        'int64': '<int>', 'int32': '<int>',
        'float64': '<dbl>', 'float32': '<dbl>',
        'object': '<chr>', 'string': '<chr>',
        'category': '<fct>',
        'bool': '<lgl>',
        'datetime64[ns]': '<dttm>',
        'timedelta64[ns]': '<time>'
    }
    max_col_len = max(len(col) for col in df.columns) if df.columns.any() else 0
    dtype_strs = [DTYPE_MAP.get(str(dt), f"<{str(dt)}>") for dt in df.dtypes]
    max_dtype_len = max(len(dt) for dt in dtype_strs) if dtype_strs else 0
    for i, col_name in enumerate(df.columns):
        col_series = df[col_name]
        col_dtype = col_series.dtype
        dtype_str = dtype_strs[i]
        prefix = f"$ {col_name:<{max_col_len}}  {dtype_str:<{max_dtype_len}} "
        if col_series.empty or col_series.isnull().all():
            values_str = "NA"
        elif is_datetime64_any_dtype(col_dtype):
            unique_years = np.sort(col_series.dropna().dt.year.unique())
            values_str = "Years: " + ", ".join(map(str, unique_years))
        elif is_string_dtype(col_dtype):
            unique_vals = np.sort(col_series.dropna().unique())
            count_str = f"({len(unique_vals)} unique)"
            str_list = [f'"{v}"' for v in unique_vals]
            values_str = f'{", ".join(str_list)} {count_str}'
        else:
            values_str = _format_default_preview(col_series, max_n)
        available_width = width - len(prefix)
        if len(values_str) > available_width:
            cutoff = max(0, available_width - 4)
            values_str = values_str[:cutoff] + " ..."
        print(prefix + values_str) 