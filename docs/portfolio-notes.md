# Portfolio Notes

This repository is a public, synthetic-data demonstration intended for Research Engineer, Materials AI, and Scientific ML portfolio review.

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

## Why The Demo Uses Synthetic Data

The synthetic-only scope makes the repository safe for public review while still showing engineering practices that matter in real scientific ML systems: provenance, scale handling, metric reporting, visual audit artifacts, testability, and release controls.

## Extension Path

The public architecture is intentionally modular. In a private or post-publication setting, the deterministic detector and segmenter can be replaced by trained detector/segmentation components while preserving the same manifest, measurement, reporting, and safety boundaries.
