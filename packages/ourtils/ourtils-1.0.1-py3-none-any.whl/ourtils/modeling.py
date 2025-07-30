"""
All things modeling
"""

from functools import cached_property

import pandas as pd
import seaborn as sns
import patsy
from matplotlib import pyplot as plt

from statsmodels.regression import linear_model as lm
from statsmodels.formula import api as smf
from statsmodels.api import graphics as smg

from scipy import stats

from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_validate


def standardize(numbers: pd.Series) -> pd.Series:
    """Safely standardizes a series."""
    if numbers.dtype == "object":
        return numbers
    return stats.zscore(numbers)


class RegressionResult:
    """Represents a single model"""

    def __init__(self, key: str, formula: str, description: str, data: pd.DataFrame):
        self.key = key
        self.description = description
        self.formula = formula
        self.data = data

    @property
    def y_variable(self) -> str:
        if len(self.model_descr.lhs_termlist) != 1:
            raise Exception("Multiple ys found in formula, not handling...")
        return self.model_descr.lhs_termlist[0].name()

    @cached_property
    def fitted_model(self) -> lm.RegressionResultsWrapper:
        return smf.ols(self.formula, data=self.data).fit()

    @cached_property
    def standardized_fitted_model(self):
        """Standardizes data before fitting."""
        standardized_data = self.data.apply(standardize)
        return smf.ols(self.formula, data=standardized_data).fit()

    @property
    def model_descr(self):
        return patsy.ModelDesc.from_formula(self.formula)

    @property
    def summary(self):
        return self.fitted_model.summary()

    @cached_property
    def regression_influences(self):
        return self.fitted_model.get_influence()

    def tag_dataframe(self, _df) -> pd.DataFrame:
        return _df.assign(
            key=self.key, description=self.description, formula=self.formula
        )

    def get_param_df(self, standardize=True) -> pd.DataFrame:
        if standardize:
            fitted_model = self.standardized_fitted_model
        else:
            fitted_model = self.fitted_model

        model_df = pd.DataFrame(
            {key: getattr(fitted_model, key) for key in ("params", "bse", "pvalues")}
        )
        model_df = self.tag_dataframe(model_df)
        model_df.reset_index(inplace=True)
        model_df.rename(columns={"index": "coef"}, inplace=True)
        return model_df

    @property
    def diagnostic_df(self) -> pd.DataFrame:
        _data = self.data.copy()

        # Distance from average, could be extreme X and Y...
        leverages = self.regression_influences.hat_matrix_diag

        # A measure of how much the model changes without this point
        cooks_values, cooks_ps = self.regression_influences.cooks_distance

        _data["predicted"] = self.fitted_model.fittedvalues
        _data["residual"] = self.fitted_model.resid
        _data["leverage"] = leverages
        _data["cooks_d"] = cooks_values
        _data["cooks_pvalue"] = cooks_ps
        _data = self.tag_dataframe(_data)
        return _data

    @property
    def info_df(self) -> pd.DataFrame:
        base_dict = {
            "key": self.key,
            "formula": self.formula,
            "description": self.description,
        }
        fitted_model_attrs = (
            "rsquared",
            "rsquared_adj",
            "nobs",
            "mse_model",
            "ssr",
            "mse_resid",
            "fvalue",
            "f_pvalue",
        )
        for attr in fitted_model_attrs:
            base_dict[attr] = getattr(self.fitted_model, attr)

        return pd.DataFrame.from_dict([base_dict])

    def get_n_most_influential_points(self, n=5):
        return self.diagnostic_df.sort_values(by="cooks_d", ascending=False).head(n)

    def plot_scatter(self, x_val: str, y_val=None, highlight_influence=False, **kwargs):
        if y_val is not None:
            y = y_val
        else:
            y = self.y_variable

        sns.lmplot(
            x=x_val,
            y=y,
            data=self.data,
            x_jitter=0.25,
            y_jitter=0.25,
            scatter_kws={"alpha": 0.3},
            **kwargs,
        )
        if highlight_influence:
            sns.scatterplot(
                data=self.data.loc[
                    lambda x: x.index.isin(self.idx_most_influential(5))
                ],
                x=x_val,
                y=y,
                color="red",
            )

    def plot_coefs(self, *args, **kwargs):
        bar_data = self.get_param_df(*args, **kwargs).query('coef != "Intercept"')
        axes = sns.barplot(data=bar_data, x="coef", y="params", hue="coef")
        for i in range(len(bar_data)):
            axes.errorbar(
                x=i,
                y=bar_data["params"].iloc[i],
                yerr=bar_data["bse"].iloc[i],
                fmt="none",
                color="black",
                capsize=5,
            )
        axes.axhline(y=0, color="black")

    def idx_most_influential(self, n):
        return self.get_n_most_influential_points(n).index

    def plot_n_influential(self, x_val: str, n: int, title=None, ax=None) -> None:
        """Plots the n most influential points."""
        if ax is None:
            fig, ax = plt.subplots()
        else:
            fig = plt.gcf()

        if title is not None:
            ax.set_title(title)
        else:
            ax.set_title(f"{n} most influential points ('{self.y_variable}')")

        idx_most_influential = self.idx_most_influential(n)
        standard_points = self.data.loc[lambda x: ~x.index.isin(idx_most_influential)]
        influentials = self.data.loc[lambda x: x.index.isin(idx_most_influential)]

        min_x = self.data[x_val].min()
        max_x = self.data[x_val].max()
        ax.set_xlim([min_x, max_x])
        sns.stripplot(
            standard_points, x=x_val, y=self.y_variable, alpha=0.3, jitter=0.5, ax=ax
        )
        sns.stripplot(
            influentials,
            x=x_val,
            y=self.y_variable,
            color="red",
            ax=ax,
            alpha=1,
            jitter=1,
        )
        return fig, ax, idx_most_influential

    def plot_qq(self):
        smg.qqplot(self.fitted_model.resid)

    def plot_leverage_vs_resids(self):
        smg.plot_leverage_resid2(self.fitted_model)

    def plot_partial_regression(self):
        smg.plot_partregress_grid(self.fitted_model)


class RegResultCollection:
    """Represents a collection of regression models."""

    def __str__(self):
        return f"Regression results for {len(self.reg_results)} model(s)."

    @classmethod
    def build_from_mapper(cls, input_data: pd.DataFrame, model_mapper: list[tuple]):
        """
        Creates a RegResultCollection from a dictionary

        model_mapper: A dictionary of:
        ```python
        import pandas as pd
        {
            (key, formula): model description
        }
        ```
        input_data: The input dataframe to fit the model on
        """
        all_results = []
        seen_keys = set()
        for key, formula, description in model_mapper:
            if key in seen_keys:
                raise Exception(f"Duplicate model key '{key}' found!")
            all_results.append(RegressionResult(key, formula, description, input_data))
            seen_keys.add(key)

        return cls(all_results)

    def batch_plot_regs(self, x_var: str, n=10):
        fig, axes = plt.subplots(1, len(self.reg_results), figsize=(15, 5))
        for i, res in enumerate(self.reg_results):
            res.plot_n_influential(x_var, res.y_variable, n, True, ax=axes[i])
        return fig, axes

    def __init__(self, reg_results: list[RegressionResult]):
        self.reg_results = reg_results

    def __getitem__(self, item) -> RegressionResult:
        """Returns a reg result"""
        try:
            return self._models[item]
        except KeyError as e:
            raise Exception(f"No model with key={e}")

    def coef_dataframe(self, *args, **kwargs) -> pd.DataFrame:
        """Returns model summaries as a dataframe"""
        output = pd.concat(
            [result.get_param_df(*args, **kwargs) for result in self.reg_results]
        ).sort_values(by="coef")
        return output

    def _concat_frames(self, result_attr_name: str) -> pd.DataFrame:
        return pd.concat(
            [getattr(result, result_attr_name) for result in self.reg_results]
        )

    @property
    def model_summary(self):
        return self._concat_frames("info_df")

    @property
    def rowlevel_data(self) -> pd.DataFrame:
        return self._concat_frames("diagnostic_df")

    @property
    def _models(self) -> dict:
        return {result.key: result for result in self.reg_results}

    def plot_coefs(self, show_nums=True, scale_by=None, *args, **kwargs):
        """Plots the coefficients of each model as a bar chart with error bars."""
        bar_data = (
            self.coef_dataframe(*args, **kwargs).query('coef != "Intercept"')
            # ax.patches are in formula order
            .sort_values(by="formula")
        )

        if scale_by:
            bar_data["params"] = bar_data["params"] * scale_by

        n_total_bars = bar_data[["key", "coef"]].drop_duplicates().shape[0]

        axes = sns.barplot(data=bar_data, x="coef", y="params", hue="formula")
        axes.axhline(y=0, color="black")

        if scale_by:
            axes.set_title(f"Scaled by {scale_by}")

        # Remove any bonus patches that may get drawn
        correct_patches = [
            patch for patch in axes.patches if patch.get_x() and patch.get_height()
        ]
        if n_total_bars != len(correct_patches):
            raise Exception(
                f"Should see {n_total_bars} bar(s), but am seeing {len(correct_patches)} bar(s)"
            )

        if not show_nums:
            return axes

        def sign(x):
            if x < 0:
                return -1
            elif x > 0:
                return 1
            return 0

        for i, patch in enumerate(correct_patches):
            row_data = bar_data.iloc[i]
            bse = row_data["bse"]
            estimate = row_data["params"]
            x = patch.get_x()
            y = patch.get_height()
            width = patch.get_width()
            x_val = x + (width / 2)
            axes.text(
                x_val,
                sign(estimate) * 0.02 * (scale_by or 1),
                f"{estimate:.2f}",
                ha="center",
                va="center",
            )
            if scale_by:
                # Skip error bars if scaling
                continue
            axes.errorbar(x_val, y, yerr=bse, color="black", capsize=5)
            axes.text(
                x_val,
                y + (sign(estimate) * (bse + 0.02)),
                f"{bse:.3f}",
                ha="center",
                va="center",
            )

        return axes


class Sklearner:
    def __init__(self, X, y, preprocessing_pipeline, models: list):
        self.X = X
        self.y = y
        self.preprocessing_pipeline = preprocessing_pipeline
        self.models = models

    def create_cv_results(self, *args, **kwargs) -> pd.DataFrame:
        output = []
        for model in self.models:
            pipeline_with_model = make_pipeline(self.preprocessing_pipeline, model)
            results = cross_validate(
                pipeline_with_model, self.X, self.y, *args, **kwargs
            )
            _res = pd.DataFrame(results)
            _res["_model"] = str(model)
            output.append(_res)

        return pd.concat(output)
