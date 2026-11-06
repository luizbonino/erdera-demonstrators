"""End-to-end test of the D5 chain against a local fixture server.

The fixtures mimic an FDP serving a dataset and its distribution as separate
Turtle resources. `dataset.ttl` points at a CSV. `hd_dataset.ttl` is shaped
like the WP13 Huntington record: blank-node publisher, an access and a
download distribution, and a download URL that redirects, as GEO's does, to a
gzipped matrix. The test starts a local HTTP server, rewrites the {BASE}
placeholder in the fixtures to that server's address, and runs the same calls
the notebook makes.
"""

from __future__ import annotations

import http.server
import socketserver
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

from src import vpfollow  # noqa: E402

FIXTURES = ROOT / "fixtures"


class _Quiet(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".ttl": "text/turtle",
        ".csv": "text/csv",
    }

    def do_GET(self):
        # GEO serves supplementary files from /geo/download/?...&file=... by
        # redirecting to the file itself.
        if self.path.startswith("/geo/download/"):
            self.send_response(301)
            self.send_header("Location", "/GSE0_counts.txt.gz")
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, *args):  # silence the server
        pass


@pytest.fixture(scope="module")
def served(tmp_path_factory):
    """Serve a copy of the fixtures with {BASE} filled in."""
    www = tmp_path_factory.mktemp("www")
    handler = lambda *a, **k: _Quiet(*a, directory=str(www), **k)  # noqa: E731
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        base = f"http://127.0.0.1:{httpd.server_address[1]}"
        for src in FIXTURES.iterdir():
            text = src.read_bytes()
            if src.suffix == ".in":
                text = text.decode().replace("{BASE}", base).encode()
                (www / src.name[: -len(".in")]).write_bytes(text)
            else:
                (www / src.name).write_bytes(text)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        yield base
        httpd.shutdown()


def test_follow_reads_dataset_and_distribution(served):
    dataset, distributions = vpfollow.follow(f"{served}/dataset.ttl")
    assert dataset.title.startswith("Synthetic CAKUT")
    assert dataset.publisher_name == "Synthetic Rare Kidney Research Group"
    assert "http://www.orpha.net/ORDO/Orphanet_93545" in dataset.themes
    assert dataset.license == "https://w3id.org/ejp-rd/resources/licenses/v1.0/"
    assert len(distributions) == 1
    dist = distributions[0]
    assert dist.media_type == "text/csv"
    assert dist.download_url == f"{served}/proteome.csv"


def test_choose_prefers_download_url():
    a = vpfollow.DistributionRecord(iri="a", access_url="http://x/a")
    b = vpfollow.DistributionRecord(iri="b", download_url="http://x/b")
    assert vpfollow.choose([a, b]).iri == "b"
    assert vpfollow.choose([a]).iri == "a"
    assert vpfollow.choose([]) is None


def test_download_and_load(served, tmp_path):
    _, distributions = vpfollow.follow(f"{served}/dataset.ttl")
    chosen = vpfollow.choose(distributions)
    path = vpfollow.download(chosen.data_url, tmp_path / "downloads")
    assert path.name == "proteome.csv"
    table = vpfollow.load_table(path)
    assert list(table.columns)[:2] == ["protein", "group"]
    assert len(table) == 8
    means = table.groupby("group")[["sample_1", "sample_2", "sample_3", "sample_4"]].mean()
    assert set(means.index) == {"CAKUT", "control"}


def test_prov_record(served, tmp_path):
    dataset, distributions = vpfollow.follow(f"{served}/dataset.ttl")
    chosen = vpfollow.choose(distributions)
    path = vpfollow.download(chosen.data_url, tmp_path / "downloads")
    started = datetime(2026, 11, 6, 10, 0, tzinfo=timezone.utc)
    g = vpfollow.prov_graph(dataset, chosen, path, started)
    ttl = g.serialize(format="turtle")
    assert "prov:used" in ttl
    assert dataset.iri in ttl
    assert chosen.data_url in ttl
    assert "prov:wasDerivedFrom" in ttl


def _response(url, headers):
    r = vpfollow.requests.Response()
    r.url = url
    r.headers.update(headers)
    return r


def test_filename_from_disposition_redirect_or_type():
    # Zenodo: Content-Disposition names the file.
    r = _response("https://zenodo.org/records/1/files/x?download=1",
                  {"Content-Disposition": "attachment; filename=CAKUT_miRNA.xlsx"})
    assert vpfollow._filename(r) == "CAKUT_miRNA.xlsx"
    # GEO: the download URL redirects, and response.url is the real file.
    r = _response("https://ftp.ncbi.nlm.nih.gov/geo/series/GSE64nnn/GSE64810/suppl/GSE64810_counts.txt.gz", {})
    assert vpfollow._filename(r) == "GSE64810_counts.txt.gz"
    # Nothing but a media type.
    r = _response("https://example.org/download/", {"Content-Type": "text/csv"})
    assert vpfollow._filename(r) == "download.csv"


def test_wp13_shaped_record_to_comparison(served, tmp_path):
    from src import firstlook

    dataset, distributions = vpfollow.follow(f"{served}/hd_dataset.ttl")
    # Blank-node publisher: the name is found, and there is no IRI to show.
    assert dataset.publisher_name == "NCBI"
    assert dataset.publisher_iri is None
    assert "http://www.orpha.net/ORDO/Orphanet_399" in dataset.themes
    assert len(distributions) == 2
    chosen = vpfollow.choose(distributions)
    assert chosen.iri == f"{served}/hd_download.ttl"
    # The download URL has no file name in its path; the redirect target does.
    path = vpfollow.download(chosen.data_url, tmp_path / "downloads")
    assert path.name == "GSE0_counts.txt"
    matrix = firstlook.as_matrix(vpfollow.load_table(path))
    assert matrix.shape == (4, 5)
    assert matrix.index.name == "feature"
    groups = firstlook.two_groups(firstlook.groups_from_names(matrix.columns, r"^([CH])_"), r"^C$", "HD")
    out = firstlook.compare(matrix, groups)
    assert out.attrs["n"] == {"control": 3, "HD": 2}
    assert out.index[0] == "ENSG00000000001.1"


def test_workbook_sheets(tmp_path):
    import pandas as pd

    path = tmp_path / "book.xlsx"
    with pd.ExcelWriter(path) as xl:
        pd.DataFrame({"about": ["readme"]}).to_excel(xl, sheet_name="Background", index=False)
        pd.DataFrame({"ID_REF": ["m1"], "s1": [1.0]}).to_excel(xl, sheet_name="Data matrix", index=False)
    assert vpfollow.sheets(path) == ["Background", "Data matrix"]
    assert list(vpfollow.load_table(path, sheet="Data matrix").columns) == ["ID_REF", "s1"]
    assert list(vpfollow.load_table(path).columns) == ["about"]
