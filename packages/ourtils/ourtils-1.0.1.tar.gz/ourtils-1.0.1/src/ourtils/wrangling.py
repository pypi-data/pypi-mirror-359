"""
Data wrangling functions, typically with pandas
"""

import random
from typing import Literal, Union, Callable

import numpy as np
import pandas as pd
import operator as pyop


def send_column_to(
    dat: pd.DataFrame,
    move_cols: Union[list[str], str],
    send_to: Literal["front", "back"] = "front",
) -> pd.DataFrame:
    """
    Sends a column / columns to the front / back of a dataframe
    """
    if isinstance(move_cols, str):
        move_cols = [move_cols]

    leftovers = [col for col in dat.columns if col not in move_cols]
    if send_to == "front":
        cols = move_cols + leftovers
    elif send_to == "back":
        cols = leftovers + move_cols
    else:
        raise Exception(f"send_to must be 'front' or 'back', not {send_to}")
    return dat[cols]


def compute_distinct_values(dat: pd.DataFrame) -> pd.DataFrame:
    """Gets value counts of all non-numeric columns in a dataframe."""
    return (
        dat.select_dtypes(exclude=[np.number])
        .melt()
        .groupby("variable")["value"]
        .value_counts()
        .reset_index()
        .sort_values(by=["variable", "count"], ascending=False)
        .set_index("variable")
    )


def compute_pct_unique(series: pd.Series) -> float:
    """Returns the % of unique values of a series. This function will attempt
    to convert the series argument to a series.
    """
    if not isinstance(series, pd.Series):
        print(f"Attempting to convert {type(series)} to a {pd.Series}")
        series = pd.Series(series)
    return series.nunique() / series.size


def crosstab(dat: pd.DataFrame, group_by_vars, count_var) -> pd.DataFrame:
    """Computes pct / counts of count_var by group_by_vars

    crosstab(grouped, ['sex'], 'category')
    """
    a = dat.groupby(group_by_vars)[count_var].value_counts(normalize=True).reset_index()
    b = dat.groupby(group_by_vars)[count_var].value_counts().reset_index()
    return a.merge(b, on=group_by_vars + [count_var])


def sort_col_manually(input_df: pd.DataFrame, col_name: str, ordered_values: list):
    """Sorts a column in a dataframe in a manual order

    Example
    -------
    sort_col_manually(my_data, 'variable', ['first', 'second', 'third'])
    """
    all_values = input_df[col_name].unique()
    # Enable partial ordering (just moving things to the front)
    ordered_values = ordered_values + [
        val for val in all_values if val not in ordered_values
    ]
    input_df[col_name] = input_df[col_name].astype(
        pd.api.types.CategoricalDtype(categories=ordered_values, ordered=True)
    )
    input_df.sort_values(by=col_name, inplace=True)
    return input_df


def _try_get_operator(operator_name: str) -> Callable:
    try:
        return getattr(pyop, operator_name)
    except AttributeError:
        raise Exception(f'Could not find operator with name: "{operator_name}"')


def cols_with_n_distinct_values(df, n_unique, op_name: str = "le") -> pd.Series:
    """Shows columns with a certain number of unique values"""
    operation_fn = _try_get_operator(op_name)
    counts = df.apply(pd.Series.nunique)
    return counts[operation_fn(counts, n_unique)]


def filter_cols(
    data,
    n_distinct_thresh=3,
    selected_dtypes=None,
    applicator="both",
) -> pd.DataFrame:
    """Filters a dataframe based on distinct counts, OR using select_include"""
    dis_cols = set(cols_with_n_distinct_values(data, n_distinct_thresh).index.to_list())

    obj_cols = {}
    if selected_dtypes:
        obj_cols = set(data.select_dtypes(include=selected_dtypes).columns)

    cols_to_include = list(dis_cols.union(obj_cols))

    if not cols_to_include:
        raise Exception("That filtering didnt return anything!")

    return data[cols_to_include]


def shout(df: pd.DataFrame, msg: str = None) -> pd.DataFrame:
    """A simple function to be used with ``pd.pipe`` to print out
    the size of a dataframe and an optional message.

    :param df: The input dataframe
    :param msg: The message you want to print

    :returns: The original dataframe

    Example:
        .. ipython:: python

            from ourtils.wrangling import shout
            output = (
                pd.DataFrame([{'a': 10}, {'a': 15}, {'a': 20}])
                .pipe(shout, 'Starting pipeline')
                .loc[lambda x: x['a'] >= 15]
                .pipe(shout, 'After filtering')
            ); output
    """
    msg = f"{df.shape}: {msg or ''}"
    print(msg)
    return df


def collapse_multiindex(df: pd.DataFrame, sep: str = "_") -> pd.DataFrame:
    """Collapses a multi-index, this usually happens after some sort of aggregation.

    Currently only supports an index that's nested 1 level (so 2 levels)

    :param df: The input dataframe
    :param sep: A delimiter to use when joining the index values
    """
    _df = df.copy()
    index = _df.columns
    nlevels = index.nlevels
    assert nlevels == 2, f"Collapsing {nlevels} levels isn't handled yet."
    assert type(index) is pd.MultiIndex, "You must pass a dataframe with a multi-index."
    _df.columns = [sep.join([str(x) for x in v]) for v in index.values]
    _df.reset_index(inplace=True)
    return _df


def squish(
    df: pd.DataFrame,
    index_var: Union[str, list[str]],
    col_sep: str = "_",
    agg_func: Callable = list,
) -> pd.DataFrame:
    """Reshapes wide data into long format and adds a "group" column.

    :param df: The input dataframe
    :param index_var: The column or columns that uniquely identify
    :param col_sep: The thing to split the columns on
    :param agg_func: The function to use to aggregate the values. Defaults to a simple list

    Example:
        .. ipython:: python

            import pandas as pd
            from ourtils.wrangling import squish
            df = pd.DataFrame(
                columns=['index_var', 'a_1', 'a_2', 'b_1', 'b_2', 'b_3'],
                data=[
                    (1, 2, 3, 4, 5, 6),
                    (10, 20, 30, 40, 50, 60)
                ]
            )
            df

            df.pipe(squish, 'index_var')
    """
    if not isinstance(index_var, list):
        index_var = [index_var]

    def _try_split_column(colname: str) -> Union[str, None]:
        try:
            return colname.split(col_sep)[-2]
        except IndexError:
            return colname

    return (
        df.melt(id_vars=index_var, value_name="value", var_name="variable")
        .assign(group=lambda x: x["variable"].apply(_try_split_column))
        .groupby(index_var + ["group"], group_keys=False)["value"]
        .apply(lambda x: agg_func(x))
        .reset_index()
    )


def filter_random(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Returns the dataframe filtered to a random value of col.

    :param df: The input dataframe
    :param col: The column to pick a random value from
    """
    val = random.choice(df[col])
    return df.loc[lambda x: x[col] == val]


def create_column(
    df: pd.DataFrame, colname: str, func: Callable, *args, **kwargs
) -> pd.DataFrame:
    """Creates a new column using a function that takes column names as strings.

    :param df: The input dataframe
    :param colname: The name of the column you want to create
    :param func: The function to apply to the columns
    :param args: Column names to pass into ``func``


    Example:
        .. ipython:: python

            from ourtils.wrangling import create_column
            df = pd.DataFrame({
                'first': ['myfirst'],
                'last': ['mylast']
            })
            def create_name(first: str, last: str) -> str:
                return f'{last}, {first}'

            df.pipe(create_column, 'mynewcolumn', create_name, 'first', 'last')
    """
    return df.assign(
        # Need to do x.apply(lambda x: func(x['col1'], x['col2'], ..., mykwarg=15))
        __newcol=lambda x: x.apply(
            lambda x: func(
                *[x[arg] for arg in args],
                **{kwarg: value for kwarg, value in kwargs.items()},
            ),
            axis=1,
        )
    ).rename(columns={"__newcol": colname})


class ColumnSpec:
    """
    Specification for an individual column.
    """

    def __init__(
        self,
        col_names: Union[str, list[str]],
        mapping: dict,
        use_numeric_order=False,
        cat_overrides=None,
    ):
        if isinstance(col_names, str):
            self.col_names = [col_names]
        else:
            self.col_names = col_names
        self.mapping = mapping
        self.use_numeric_order = use_numeric_order
        self.cat_overrides = cat_overrides

    def as_category(self) -> pd.Categorical:
        if self.cat_overrides is not None:
            categories = self.cat_overrides
        else:
            categories = self.mapping.values()
        return pd.CategoricalDtype(categories, ordered=self.use_numeric_order)

    def apply_to_series(self, series: pd.Series) -> pd.Series:
        cat_type = self.as_category()
        return series.map(self.mapping).astype(cat_type)


class SpecCollection:
    """A collection of columnspecs."""

    def __init__(self, specs: list[ColumnSpec]):
        self.specs = specs

    def __getitem__(self, key) -> ColumnSpec:
        try:
            spec = [spec for spec in self.specs if key in spec.col_names][0]
        except IndexError:
            raise KeyError(f"No spec found for '{key}'")
        return spec

    def _map_to_series(self, series: pd.Series) -> pd.Series:
        try:
            spec = self[series.name]
            return spec.apply_to_series(series)
        except KeyError:
            return series

    def map_to_dataframe(self, data: pd.DataFrame) -> pd.DataFrame:
        """Applies all column specs to a dataframe."""
        return data.apply(self._map_to_series)


if __name__ == "__main__":
    dat = pd.DataFrame(
        {"grp": ["first", "second", "second", "third"], "score": [1, 1, 2, 2]}
    )
    sort_col_manually(dat, "grp", ["second", "third"])
    print(dat)
