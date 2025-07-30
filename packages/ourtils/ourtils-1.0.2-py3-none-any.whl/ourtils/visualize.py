"""
All things data visualization
"""

from typing import Union
import plotly.express as px
import pandas as pd
from matplotlib import pyplot as plt
from .wrangling import compute_pct_unique, crosstab


def plot_pct_uniqueness(dat: pd.DataFrame) -> tuple:
    """
    Draws a plot that counts the unique values in a dataframe.
    Returns a tuple of the matplotlib figure / axis objects so they
    can be further customized
    """
    fig, ax = plt.subplots()
    unique_pct = dat.apply(compute_pct_unique)
    unique_pct.plot(kind="barh", xlim=(0, 1), ax=ax)
    # n unique values for each column
    pct_value_mapper = dat.apply(pd.Series.nunique).to_dict()
    ytick_labels = [tick.get_text() for tick in ax.get_yticklabels()]
    print(pct_value_mapper)
    for i, rect in enumerate(ax.patches):
        X_COORD = rect.get_width() + 0.05
        Y_COORD = rect.get_y() + rect.get_height() / 2
        pct_unique = pct_value_mapper[ytick_labels[i]]
        txt = f"{round(rect.get_width(), 3)} ({pct_unique})"
        ax.text(X_COORD, Y_COORD, txt, ha="left", va="center_baseline")

    ax.set_title(f"Uniqueness ({dat.shape[0]} total rows)")
    ax.set_xticks([0, 1])
    ax.tick_params(length=0)
    ax.set_xticklabels(["All Values Identical (0)", "All Values Unique (1)"])
    return fig, ax


def plot_pct(
    data,
    group_by_vars: Union[list, str],
    target_var: str,
    use_proportion=True,
    plotly_kwargs=None,
    auto_show=True,
) -> tuple:
    """Plots percentage counts by group. Returns"""
    plotly_kwargs = plotly_kwargs or {}
    facet_kwargs = {}

    if isinstance(group_by_vars, str):
        group_by_vars = [group_by_vars]

    y = group_by_vars[0]
    if len(group_by_vars) > 1:
        facet_kwargs["facet_col"] = group_by_vars[1]
    if len(group_by_vars) > 2:
        facet_kwargs["facet_row"] = group_by_vars[2]
    if len(group_by_vars) > 3:
        raise ValueError("Impossible to visualize > 3 groupings!")

    # Show all labels by default
    hd = {"proportion": ":.1%", "count": True}
    for col in group_by_vars:
        hd[col] = True

    summary_data = crosstab(data, group_by_vars, target_var)
    x_var = "proportion" if use_proportion else "count"
    fig = px.bar(
        summary_data, x=x_var, y=y, color=target_var, **facet_kwargs, **plotly_kwargs
    )
    if auto_show:
        fig.show()
    return fig, summary_data
