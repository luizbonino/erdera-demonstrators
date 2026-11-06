"""The two-group comparison the D5 notebook runs on the downloaded matrix."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import firstlook  # noqa: E402

TABLE = pd.DataFrame({
    "ID_REF": ["m1", "m2", "m3"],
    "a": [1.0, 5.0, 2.0], "b": [3.0, 5.0, 2.0],   # cases
    "c": [1.0, 1.0, 2.0], "d": [1.0, 1.0, 2.0],   # controls
    "e": [9.0, 9.0, 9.0],                          # no group
})


def test_groups_from_sample_sheet_strip_and_collapse():
    sheet = pd.DataFrame({
        "Sample name": ["a", "b", "c", "d", None, "[1] footnote"],
        "characteristics: group": ["Severe CAKUT", "CAKUT ", "Control (non-CAKUT)", "Control (non-CAKUT)", None, None],
    })
    labels = firstlook.groups_from_sheet(sheet, "Sample name", "characteristics: group")
    assert labels.to_dict() == {"a": "Severe CAKUT", "b": "CAKUT", "c": "Control (non-CAKUT)", "d": "Control (non-CAKUT)"}
    groups = firstlook.two_groups(labels, r"^Control", "CAKUT")
    assert groups.value_counts().to_dict() == {"CAKUT": 2, "control": 2}


def test_groups_from_names():
    labels = firstlook.groups_from_names(["C_0001", "H_0002", "other"], r"^([CH])_")
    assert labels.to_dict() == {"C_0001": "C", "H_0002": "H"}
    assert firstlook.two_groups(labels, r"^C$", "HD").to_dict() == {"C_0001": "control", "H_0002": "HD"}


def test_compare_sorts_by_size_of_difference_and_skips_ungrouped():
    matrix = firstlook.as_matrix(TABLE)
    groups = pd.Series({"a": "CAKUT", "b": "CAKUT", "c": "control", "d": "control"})
    out = firstlook.compare(matrix, groups)
    assert list(out.index) == ["m2", "m1", "m3"]
    assert out.loc["m2", "difference"] == 4.0
    assert out.loc["m3", "difference"] == 0.0
    assert out.attrs["n"] == {"CAKUT": 2, "control": 2}


def test_compare_needs_a_control_group():
    matrix = firstlook.as_matrix(TABLE)
    with pytest.raises(ValueError):
        firstlook.compare(matrix, pd.Series({"a": "x", "c": "y"}))
