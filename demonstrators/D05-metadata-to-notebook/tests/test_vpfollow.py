"""End-to-end test of the D5 chain against a local fixture server.

The fixtures mimic an FDP serving a dataset and its distribution as separate
Turtle resources, with the distribution pointing at a CSV. The test starts a
local HTTP server, rewrites the {BASE} placeholder in the fixtures to that
server's address, and runs the same calls the notebook makes.
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
    assert "http://www.orpha.net/ORDO/Orphanet_93546" in dataset.themes
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
