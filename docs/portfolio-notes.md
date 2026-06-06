# Portfolio Notes

This repository is a public portfolio demo for Research Engineer, Materials AI, and Scientific ML review. The runnable workflow uses synthetic data. The repo also includes one cropped model-result preview PNG.

## What It Demonstrates

- Scientific image-analysis workflow design from data generation through reviewable outputs.
- Python package structure with CLI entrypoints and tests.
- Manifest-based provenance, relative path handling, allowed-use metadata, and SHA-256 validation.
- Scale-aware particle measurements for microscopy-style outputs.
- Detector-prompted segmentation architecture with replaceable detector and segmenter modules.
- Review overlay generation for human inspection and QC.
- Release hygiene through `.gitignore`, `CITATION.cff`, documentation, and a safety scanner.

## What It Does Not Claim

- It does not claim state-of-the-art model performance.
- It does not expose or summarize private research datasets.
- It does not include trained weights, checkpoints, raw microscopy formats, private annotations, lab notes, cluster scripts, or manuscript-specific conclusions.
- It does not use code, data, images, README text, or weights from related public projects.

## Why The Runnable Demo Uses Synthetic Data

Synthetic runnable data keeps the public code path reproducible. It still exercises the engineering pieces that matter in scientific ML systems: provenance, scale handling, metric reporting, visual audit artifacts, tests, and release controls.

## Extension Path

The public architecture is modular. A private or post-publication release can replace the deterministic detector and segmenter with trained components while keeping the same manifest, measurement, reporting, and safety boundaries.
