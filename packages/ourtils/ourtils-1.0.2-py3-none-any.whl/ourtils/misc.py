"""
Other misc items
"""

import os
from pathlib import Path

import pandas as pd


def create_analysis_notes(filename: Path, df: pd.DataFrame) -> None:
    """Creates a template markdown file to start making notes"""
    notes = [
        "# Analysis notes",
        "",
        "## Key Analysis Questions",
        "",
        "## Key Findings",
        "",
        "## Outstanding Questions",
        "",
        "## Dataset Info",
        "",
        f"Shape: {df.shape}",
        "",
        df.describe().to_markdown(),
        "",
        "## Columns",
        "",
    ]
    for col in df.columns:
        notes.append(f"- {col} ({df[col].dtype}): ")

    notes += [
        "",
        "## Other Notes",
        "",
    ]
    if os.path.exists(filename):
        raise Exception(f"'{filename}' already exists!!")
    with open(filename, "w") as f:
        f.writelines("\n".join(notes))
