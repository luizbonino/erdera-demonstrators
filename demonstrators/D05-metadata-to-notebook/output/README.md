# D5 output

The notebook executed with its default parameters on 2026-11-06, and what it
produced.

- `d5_metadata_to_notebook.executed.ipynb`, the notebook with its outputs.
- `top_differences.png`, the 20 genes with the largest difference of mean
  log2(count + 1) between Huntington disease and control samples.
- `prov.ttl`, the PROV-O record of the run.

The data are GEO series GSE64810, "mRNA-Seq Expression profiling of human
post-mortem BA9 brain tissue for Huntington's Disease and neurologically
normal individuals", Labadorf A, Hoss AG et al., PLoS One 2015,
PMID 26636579. The dataset record in the EJP RD WP13 FAIR Data Point states
the licence CC BY-NC 4.0. NCBI places no restrictions on the use of GEO data.

The figure is a first look, not a differential expression analysis. It
ranks genes by difference of means, with no test and no correction.

To regenerate, run the notebook in `notebook/` and copy
`notebook/output/top_differences.png` and `notebook/output/prov.ttl` here.
