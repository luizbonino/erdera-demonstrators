"""Build synthetic-registry.xlsx from the official ERDERA template and the TSVs.

The TSVs in this folder are the source of truth. This script downloads the
official template (ejp-rd-vp/resource-metadata-schema, CC0) at a pinned commit,
clears its example rows, writes the TSV rows into the matching sheets, and
saves the result, so the xlsx and the TSV forms always hold the same values.
The template's lookup sheets (Mediatypes, Languages) and its data validations
are kept.

    python build_xlsx.py            # needs openpyxl and network access
"""

from __future__ import annotations

import csv
import io
import sys
import urllib.request
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
COMMIT = "74df189"  # last change to the template, 2023-11-10
TEMPLATE = (
    "https://raw.githubusercontent.com/ejp-rd-vp/resource-metadata-schema/"
    f"{COMMIT}/template/EJPRD%20Resource%20Metadata%20template.xlsx"
)
RESOURCE_SHEETS = [
    "Organisation", "ContactPoint", "Biobank", "PatientRegistry", "Guideline",
    "Dataset", "Distribution", "DataService", "Catalog",
]
OUT = HERE / "synthetic-registry.xlsx"


def main() -> int:
    with urllib.request.urlopen(TEMPLATE, timeout=60) as response:
        wb = openpyxl.load_workbook(io.BytesIO(response.read()))

    for name in RESOURCE_SHEETS:
        ws = wb[name]
        header = [c.value for c in ws[1]]
        # Clear every row below the header: the template ships example rows
        # (hPSCreg) and a row 2 with only VPConnection filled in. Its URLs are
        # also Excel hyperlinks, which openpyxl writes back as the cell value
        # unless they are removed too.
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
            for cell in row:
                cell.value = None
                cell.hyperlink = None

        tsv = HERE / f"{name}.tsv"
        if not tsv.exists():
            continue
        with open(tsv, newline="") as fh:
            rows = list(csv.reader(fh, delimiter="\t"))
        tsv_header, data = rows[0], rows[1:]
        for column in tsv_header:
            if column not in header:
                print(f"{name}: column {column!r} is not in the template", file=sys.stderr)
                return 1
        for r, values in enumerate(data, start=2):
            for column, value in zip(tsv_header, values):
                if value != "":
                    ws.cell(row=r, column=header.index(column) + 1, value=value)

    wb.save(OUT)
    print(f"Wrote {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
