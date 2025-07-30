from collections import defaultdict
from dataclasses import dataclass
from typing import Callable
import pandas as pd


@dataclass
class SetComparison:
    only_a: set
    only_b: set
    in_both: set


def compare_sets(a: set, b: set, report=True) -> SetComparison:
    """Returns a tuple of useful differences of a set.

    Example:
        .. ipython:: python

            a = {1, 2, 3}
            b = {2, 3, 5}
            diffs.compare_sets(a, b)
    """
    if isinstance(a, list):
        a = set(a)
    if isinstance(b, list):
        b = set(b)

    in_both = a.intersection(b)
    only_a = a.difference(b)
    only_b = b.difference(a)
    if report:
        print(f"Only A: {only_a}")
        print(f"Only B: {only_b}")
        print(f"In both: {in_both}")

    return SetComparison(only_a, only_b, in_both)


class DataFrameDiffer:
    """
    A class to help compare dataframes. Deals with:

    - Matching columns
    - Filtering to differing rows

    Example:
        .. ipython:: python

            import pandas as pd
            from ourtils import diffs

            df1 = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
            df1

            df2 = pd.DataFrame({"a": [1, 2, 4], "B": [4, 5, 1], "c": [5, 6, 1]})
            df2

            # Create a DataFrameDiffer object
            diffy = diffs.DataFrameDiffer(df1, df2, "a")
            print(diffy.create_report())
            diffy.combined

    """

    lsuffix = "__left"
    rsuffix = "__right"

    @classmethod
    def create_diff(cls, row: pd.Series, cols: list[str]) -> dict:
        """Creates a dictionary that stores changes to the columns in a row.

        :param row: A row from a dataframe
        :param cols: A list of strings
        """
        _diff = defaultdict()
        for col in cols:
            b, a = row[f"{col}{cls.lsuffix}"], row[f"{col}{cls.rsuffix}"]
            if b != a:
                _diff[col] = (b, a)
        return _diff

    def __init__(
        self,
        left: pd.DataFrame,
        right: pd.DataFrame,
        join_on: list[str],
        column_cleaner: Callable = lambda x: x.strip().lower(),
    ):
        self.ldata = left.copy()
        self.rdata = right.copy()

        self.join_on = join_on
        self.column_cleaner = column_cleaner

        self.ldata.columns = [column_cleaner(col) for col in self.ldata]
        self.rdata.columns = [column_cleaner(col) for col in self.rdata]

        self.join_on = [column_cleaner(key) for key in self.join_on]

        self.columns_to_compare = [
            col for col in self.matching_columns if col not in self.join_on
        ]

        def create_message(_merge_indicator: str, diff: dict) -> str:
            """
            Creates a label based on the merge indicator as well as the changes
            that have happened to the row.
            """
            if _merge_indicator == "left_only":
                return "deleted"
            elif _merge_indicator == "right_only":
                return "inserted"
            elif diff:
                return "updated"
            return "same"

        self.combined = (
            pd.merge(
                self.ldata,
                self.rdata,
                on=self.join_on,
                indicator=True,
                how="outer",
                suffixes=(self.lsuffix, self.rsuffix),
            )
            .assign(
                diff=lambda x: x.apply(
                    lambda x: self.create_diff(x, self.columns_to_compare), axis=1
                )
            )
            .assign(
                action=lambda x: x.apply(
                    lambda x: create_message(x["_merge"], x["diff"]), axis=1
                )
            )
            .drop(columns=["_merge"])
        )

    @property
    def left_columns(self) -> set:
        return set(self.ldata.columns)

    @property
    def right_columns(self) -> set:
        return set(self.rdata.columns)

    @property
    def matching_columns(self) -> set:
        return self.left_columns.intersection(self.right_columns)

    @property
    def new_columns(self):
        return self.right_columns.difference(self.left_columns)

    @property
    def missing_columns(self):
        return self.left_columns.difference(self.right_columns)

    @property
    def comparable(self) -> pd.DataFrame:
        return self.combined

    @property
    def changed_data(self) -> pd.DataFrame:
        return self.combined.loc[lambda x: x["action"] != "same"]

    @property
    def summary_dict(self) -> dict:
        return defaultdict(
            int, self.combined["action"].value_counts(dropna=False).to_dict()
        )

    def _trim_message(self, message: str) -> str:
        return "\n".join([x.strip(" ") for x in message.splitlines() if x.strip(" ")])

    @property
    def n_inserted(self):
        return self.summary_dict["inserted"]

    @property
    def n_updated(self):
        return self.summary_dict["updated"]

    @property
    def n_deleted(self):
        return self.summary_dict["deleted"]

    @property
    def n_same(self):
        return self.summary_dict["same"]

    @property
    def summary_msg(self) -> str:
        return self._trim_message(
            f"""
        Inserted: {self.n_inserted}
        Updated: {self.n_updated}
        Deleted: {self.n_deleted}
        Same: {self.n_same}
        """
        )

    @property
    def n_changed_rows(self):
        return self.n_inserted + self.n_deleted + self.n_updated

    def create_report(self) -> str:
        """
        Returns a string report of the differences.
        """
        report = f"""
        {'-' * 15}
        ourtils.DifferenceReport
        {'-' * 15}
        Column summary:
        Removed: {self.missing_columns or ''}
        Added: {self.new_columns or ''}
        Matching: {self.matching_columns or ''}
        {'-' * 15}
        Row summary ({self.n_changed_rows} total changes):
        {self.summary_msg}
        """
        trimmed_report = self._trim_message(report)
        return trimmed_report
