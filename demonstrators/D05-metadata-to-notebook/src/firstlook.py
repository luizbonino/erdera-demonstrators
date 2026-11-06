"""A first two-group look at an omics matrix, for the D5 notebook.

The datasets D5 follows (CAKUT mirnome, Huntington transcriptomics) come as a
matrix with one row per feature (miRNA, gene) and one column per sample. The
group of each sample comes either from a sample sheet next to the matrix or
from the sample names themselves. This module turns that into a
case-versus-control table, deliberately simple: the point of D5 is getting
here from the metadata, not the statistics.
"""

from __future__ import annotations

import re

import pandas as pd


def as_matrix(table: pd.DataFrame) -> pd.DataFrame:
    """Use the first column as the feature index and keep the numeric sample columns."""
    matrix = table.set_index(table.columns[0])
    if not matrix.index.name or str(matrix.index.name).startswith("Unnamed"):
        matrix.index.name = "feature"   # GEO matrices leave the id column without a header
    return matrix.select_dtypes("number")


def groups_from_sheet(sheet: pd.DataFrame, id_column: str, group_column: str) -> pd.Series:
    """Sample id -> group label, from a sample sheet. Rows without both are dropped."""
    pairs = sheet[[id_column, group_column]].dropna()
    labels = pairs[group_column].astype(str).str.strip()
    return pd.Series(labels.values, index=pairs[id_column].astype(str).str.strip(), name="group")


def groups_from_names(samples, pattern: str) -> pd.Series:
    """Sample id -> group label, taken from the first regex group matched in each sample name."""
    out = {}
    for sample in samples:
        match = re.search(pattern, str(sample))
        if match:
            out[str(sample)] = match.group(1)
    return pd.Series(out, name="group", dtype="object")


def two_groups(groups: pd.Series, control: str, case: str) -> pd.Series:
    """Collapse group labels to two: labels matching the `control` regex, and `case` for the rest."""
    is_control = groups.str.contains(control, regex=True)
    return groups.where(~is_control, "control").where(is_control, case)


def compare(matrix: pd.DataFrame, groups: pd.Series) -> pd.DataFrame:
    """Mean per feature in each group, and the difference, sorted by its size.

    `groups` must hold exactly two labels, one of them "control". Samples in
    the matrix with no group are left out.
    """
    samples = [c for c in matrix.columns if str(c) in groups.index]
    if not samples:
        raise ValueError("No sample column of the matrix has a group.")
    labels = groups.loc[[str(c) for c in samples]]
    kinds = sorted(set(labels))
    if len(kinds) != 2 or "control" not in kinds:
        raise ValueError(f"Expected 'control' and one case group, got {kinds}.")
    case = next(k for k in kinds if k != "control")
    data = matrix[samples]
    out = pd.DataFrame(
        {
            case: data.loc[:, (labels == case).values].mean(axis=1),
            "control": data.loc[:, (labels == "control").values].mean(axis=1),
        }
    )
    out["difference"] = out[case] - out["control"]
    out = out.reindex(out["difference"].abs().sort_values(ascending=False).index)
    out.attrs["n"] = labels.value_counts().to_dict()
    out.attrs["case"] = case
    return out
