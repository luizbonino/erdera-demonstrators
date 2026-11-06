"""Follow a Virtual Platform (FAIR Data Point) dataset record to its data.

The functions here do one thing each so that the D5 notebook reads as a
story: fetch the dataset record, read what it says, follow its distributions,
pick one, download the file, and leave a provenance record behind.

Every URL the notebook touches comes out of the metadata. Nothing is typed in
except the starting dataset IRI.
"""

from __future__ import annotations

import gzip
import mimetypes
import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote, urlparse

import requests
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, PROV, RDF, RDFS, XSD

EJPRD = Namespace("http://purl.org/ejp-rd/vocabulary/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")

# Where this demonstrator's code lives, used as the PROV agent. In Luiz's
# personal GitHub account for now; it may move to the ERDERA organisation,
# and GitHub redirects transferred repositories.
AGENT_IRI = "https://github.com/luizbonino/erdera-demonstrators/tree/main/demonstrators/D05-metadata-to-notebook"

ACCEPT = (
    "text/turtle;q=1.0, application/ld+json;q=0.9, "
    "application/rdf+xml;q=0.8, application/n-triples;q=0.7"
)

_FORMAT_BY_TYPE = {
    "text/turtle": "turtle",
    "application/x-turtle": "turtle",
    "application/ld+json": "json-ld",
    "application/rdf+xml": "xml",
    "application/n-triples": "nt",
    "text/n3": "n3",
}


def _session(session: requests.Session | None) -> requests.Session:
    return session or requests.Session()


def fetch_graph(iri: str, session: requests.Session | None = None, timeout: int = 60) -> Graph:
    """GET an RDF resource with content negotiation and parse it."""
    response = _session(session).get(iri, headers={"Accept": ACCEPT}, timeout=timeout)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
    fmt = _FORMAT_BY_TYPE.get(content_type)
    if fmt is None:
        # Fall back on the file extension, then on Turtle, which FDPs serve by default.
        guessed = {".ttl": "turtle", ".jsonld": "json-ld", ".rdf": "xml", ".nt": "nt"}
        fmt = guessed.get(Path(urlparse(iri).path).suffix.lower(), "turtle")
    graph = Graph()
    graph.parse(data=response.content, format=fmt, publicID=iri)
    return graph


def _first(graph: Graph, subject: URIRef, predicate) -> str | None:
    for value in graph.objects(subject, predicate):
        return str(value)
    return None


def _all(graph: Graph, subject: URIRef, predicate) -> list[str]:
    return [str(value) for value in graph.objects(subject, predicate)]


@dataclass
class DatasetRecord:
    iri: str
    title: str | None = None
    description: str | None = None
    publisher_iri: str | None = None
    publisher_name: str | None = None
    license: str | None = None
    access_rights: str | None = None
    landing_page: str | None = None
    themes: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    distributions: list[str] = field(default_factory=list)
    types: list[str] = field(default_factory=list)


@dataclass
class DistributionRecord:
    iri: str
    title: str | None = None
    description: str | None = None
    media_type: str | None = None
    access_url: str | None = None
    download_url: str | None = None
    license: str | None = None
    access_service: str | None = None

    @property
    def data_url(self) -> str | None:
        return self.download_url or self.access_url


def describe_dataset(graph: Graph, iri: str) -> DatasetRecord:
    s = URIRef(iri)
    publisher = next(graph.objects(s, DCTERMS.publisher), None)
    publisher_name = None
    if publisher is not None:
        # The publisher is often a blank node, so look it up as the node it is.
        publisher_name = _first(graph, publisher, FOAF.name) or _first(graph, publisher, DCTERMS.title)
    return DatasetRecord(
        iri=iri,
        title=_first(graph, s, DCTERMS.title),
        description=_first(graph, s, DCTERMS.description),
        publisher_iri=str(publisher) if isinstance(publisher, URIRef) else None,
        publisher_name=publisher_name,
        license=_first(graph, s, DCTERMS.license),
        access_rights=_first(graph, s, DCTERMS.accessRights),
        landing_page=_first(graph, s, DCAT.landingPage),
        themes=_all(graph, s, DCAT.theme),
        keywords=_all(graph, s, DCAT.keyword),
        distributions=_all(graph, s, DCAT.distribution),
        types=_all(graph, s, RDF.type),
    )


def describe_distribution(graph: Graph, iri: str) -> DistributionRecord:
    s = URIRef(iri)
    return DistributionRecord(
        iri=iri,
        title=_first(graph, s, DCTERMS.title),
        description=_first(graph, s, DCTERMS.description),
        media_type=_first(graph, s, DCAT.mediaType) or _first(graph, s, DCTERMS["format"]),
        access_url=_first(graph, s, DCAT.accessURL),
        download_url=_first(graph, s, DCAT.downloadURL),
        license=_first(graph, s, DCTERMS.license),
        access_service=_first(graph, s, DCAT.accessService),
    )


def follow(dataset_iri: str, session: requests.Session | None = None) -> tuple[DatasetRecord, list[DistributionRecord]]:
    """Fetch the dataset record and every distribution it points to.

    An FDP serves each distribution as its own resource, so a distribution IRI
    that has no triples in the dataset graph is fetched separately.
    """
    session = _session(session)
    graph = fetch_graph(dataset_iri, session)
    dataset = describe_dataset(graph, dataset_iri)
    distributions: list[DistributionRecord] = []
    for dist_iri in dataset.distributions:
        dist_graph = graph
        if (URIRef(dist_iri), None, None) not in graph:
            dist_graph = fetch_graph(dist_iri, session)
        distributions.append(describe_distribution(dist_graph, dist_iri))
    return dataset, distributions


def choose(distributions: Iterable[DistributionRecord]) -> DistributionRecord | None:
    """Prefer a distribution with a download URL, then one with an access URL."""
    distributions = list(distributions)
    for dist in distributions:
        if dist.download_url:
            return dist
    for dist in distributions:
        if dist.access_url:
            return dist
    return None


def _filename(response: requests.Response) -> str:
    """The file name a server gives a download.

    Content-Disposition wins, then the last path segment of the URL after
    redirects (GEO and Zenodo both redirect to the real file), then the
    media type.
    """
    disposition = response.headers.get("Content-Disposition", "")
    match = re.search(r"filename\*?=(?:UTF-8'')?\"?([^\";]+)\"?", disposition, flags=re.I)
    if match:
        name = Path(unquote(match.group(1))).name
    else:
        name = Path(unquote(urlparse(response.url).path)).name
    if not name or "." not in name:
        ext = mimetypes.guess_extension(response.headers.get("Content-Type", "").split(";")[0]) or ""
        name = (name or "download") + ext
    return name


def download(url: str, dest_dir: str | os.PathLike, session: requests.Session | None = None, timeout: int = 300) -> Path:
    """Stream a file to dest_dir and return its path. Gzipped files are unpacked."""
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    response = _session(session).get(url, stream=True, timeout=timeout)
    response.raise_for_status()
    path = dest_dir / _filename(response)
    with open(path, "wb") as fh:
        for chunk in response.iter_content(chunk_size=1 << 16):
            fh.write(chunk)
    if path.suffix == ".gz":
        unpacked = path.with_suffix("")
        with gzip.open(path, "rb") as src, open(unpacked, "wb") as dst:
            shutil.copyfileobj(src, dst)
        return unpacked
    return path


def sheets(path: str | os.PathLike) -> list[str]:
    """The sheet names of a workbook, or [] for a delimited text file."""
    import pandas as pd

    path = Path(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return list(pd.ExcelFile(path).sheet_names)
    return []


def load_table(path: str | os.PathLike, sheet: str | int | None = None):
    """Load a downloaded table into a pandas DataFrame.

    For a workbook, `sheet` picks the sheet (the first one by default). For
    text, the delimiter is sniffed, except for .tsv and for GEO-style .txt
    files whose first line is tab-separated.
    """
    import pandas as pd

    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path, sheet_name=sheet if sheet is not None else 0)
    with open(path, encoding="utf-8", errors="replace") as fh:
        first = fh.readline()
    if suffix == ".tsv" or "\t" in first:
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path, sep=None, engine="python")


def prov_graph(
    dataset: DatasetRecord,
    distribution: DistributionRecord,
    downloaded: Path,
    started: datetime,
    ended: datetime | None = None,
    agent_iri: str = AGENT_IRI,
) -> Graph:
    """A small PROV-O record of what the notebook fetched and produced."""
    ended = ended or datetime.now(timezone.utc)
    g = Graph()
    g.bind("prov", PROV)
    g.bind("dcat", DCAT)
    g.bind("dct", DCTERMS)
    run = URIRef(f"{agent_iri}#run-{started.strftime('%Y%m%dT%H%M%SZ')}")
    agent = URIRef(agent_iri)
    # Named under the run rather than as a file:// URI, which would only mean
    # something on the machine that ran the notebook.
    local_file = URIRef(f"{run}/{downloaded.name}")
    g.add((local_file, RDFS.label, Literal(downloaded.name)))
    g.add((agent, RDF.type, PROV.SoftwareAgent))
    g.add((run, RDF.type, PROV.Activity))
    g.add((run, PROV.wasAssociatedWith, agent))
    g.add((run, PROV.startedAtTime, Literal(started.isoformat(), datatype=XSD.dateTime)))
    g.add((run, PROV.endedAtTime, Literal(ended.isoformat(), datatype=XSD.dateTime)))
    for used in (dataset.iri, distribution.iri, distribution.data_url):
        if used:
            g.add((run, PROV.used, URIRef(used)))
            g.add((URIRef(used), RDF.type, PROV.Entity))
    g.add((local_file, RDF.type, PROV.Entity))
    g.add((local_file, PROV.wasGeneratedBy, run))
    if distribution.data_url:
        g.add((local_file, PROV.wasDerivedFrom, URIRef(distribution.data_url)))
    if dataset.title:
        g.add((URIRef(dataset.iri), DCTERMS.title, Literal(dataset.title)))
    return g
