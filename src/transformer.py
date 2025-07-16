from typing import Callable, Dict, List, Any, Optional
import pandas as pd
from pandas import DataFrame


class Transformer:
    def __init__(
        self,
        func: Callable[..., DataFrame],
        required_args: Optional[List[str]] = None,
        required_column_types_by_kwarg: Optional[Dict[str, str]] = None,
    ):
        self.func = func
        self.required_args = required_args or []
        self.required_column_types_by_kwarg = required_column_types_by_kwarg or {}

    def validate(self, df: DataFrame, kwargs: Dict[str, Any]):
        # Validate required keyword arguments
        for arg in self.required_args:
            if arg not in kwargs:
                raise ValueError(f"Missing required argument: '{arg}'")

        # Validate columns referenced by keyword arguments
        for kwarg_name, expected_type in self.required_column_types_by_kwarg.items():
            col_name = kwargs.get(kwarg_name)
            if col_name not in df.columns:
                raise ValueError(
                    f"Missing column '{col_name}' in DataFrame (from kwarg '{kwarg_name}')"
                )

            actual_dtype = df[col_name].dtype
            if expected_type == "string":
                if not pd.api.types.is_string_dtype(actual_dtype):
                    raise TypeError(
                        f"Column '{col_name}' must be of type string, got '{actual_dtype}'"
                    )
            elif expected_type == "numeric":
                if not pd.api.types.is_numeric_dtype(actual_dtype):
                    raise TypeError(
                        f"Column '{col_name}' must be numeric, got '{actual_dtype}'"
                    )
            elif expected_type == "boolean":
                if not pd.api.types.is_bool_dtype(actual_dtype):
                    raise TypeError(
                        f"Column '{col_name}' must be boolean, got '{actual_dtype}'"
                    )
            else:
                raise ValueError(
                    f"Unsupported expected type '{expected_type}' for kwarg '{kwarg_name}'"
                )

    def run(self, df: DataFrame, **kwargs) -> DataFrame:
        return self.func(df, **kwargs)

    def get_metadata(self):
        ret = {}
        if self.required_args:
            ret["required_args"] = self.required_args
        if self.required_column_types_by_kwarg:
            ret["required_column_types"] = self.required_column_types_by_kwarg
        return ret


class TransformerRegistry:
    def __init__(self):
        self.registry: Dict[str, Transformer] = {}

    def register(self, name: str, transformer: Transformer):
        self.registry[name] = transformer

    def get(self, name: str) -> Optional[Transformer]:
        return self.registry.get(name)

    def list_available(self) -> List[str]:
        return list(self.registry.keys())


# Transformers functions
def filter_rows(df: DataFrame, **kwargs) -> DataFrame:
    return df.query(kwargs["condition"])


def rename_column(df: DataFrame, **kwargs) -> DataFrame:
    return df.rename(columns={kwargs["from"]: kwargs["to"]})


def uppercase_column(df: DataFrame, **kwargs) -> DataFrame:
    col = kwargs["column"]
    df[col] = df[col].str.upper()
    return df


def drop_columns(df: DataFrame, **kwargs) -> DataFrame:
    return df.drop(columns=kwargs["columns"])


def fillna_column(df: DataFrame, **kwargs) -> DataFrame:
    return df.fillna({kwargs["column"]: kwargs["value"]})


def sort_dataframe(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    by = kwargs["by"]
    ascending = kwargs.get("ascending", True)

    if isinstance(by, str):
        by = [by]

    return df.sort_values(by=by, ascending=ascending)


# Register built-in transformers
def register_builtin_transformers(registry: TransformerRegistry):
    registry.register(
        "filter", Transformer(func=filter_rows, required_args=["condition"])
    )

    registry.register(
        "rename",
        Transformer(
            func=rename_column,
            required_args=["from", "to"],
            required_column_types_by_kwarg={"from": "string"},
        ),
    )

    registry.register(
        "uppercase",
        Transformer(
            func=uppercase_column,
            required_args=["column"],
            required_column_types_by_kwarg={"column": "string"},
        ),
    )

    registry.register("drop", Transformer(func=drop_columns, required_args=["columns"]))

    registry.register(
        "fillna",
        Transformer(
            func=fillna_column,
            required_args=["column", "value"],
        ),
    )

    registry.register(
        "sort",
        Transformer(
            func=sort_dataframe,
            required_args=["by", "ascending"],
        ),
    )
