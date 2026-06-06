# Publication Companion Roadmap

This repository is a public portfolio demo. It can become a paper companion repository after the associated manuscript is public.

## Current Public Demo Scope

- Synthetic TEM-like runnable data.
- One cropped carbon-black model-result preview PNG.
- No raw research images.
- No trained weights or checkpoints.
- No private manifests or internal experiment records.
- No unpublished performance claims.
- No copied code, images, data, README text, or weights from related repositories.

## After Paper Acceptance or Publication

The repository can be extended with:

1. A tagged release matching the submitted or accepted manuscript.
2. A formal citation in `CITATION.cff`.
3. A methods configuration folder matching the paper protocol.
4. Public benchmark tables that are cleared for release.
5. Public data links, data-use instructions, or access-controlled data instructions.
6. Model-card and weight-download instructions only where redistribution is permitted.
7. Reproduction scripts that recreate paper figures from public or cleared artifacts.

## Release Hygiene Checklist

Before changing this repository from portfolio demo to paper companion:

- Run `python scripts/safety_scan.py .`.
- Confirm all data licenses and redistribution permissions.
- Confirm model-weight redistribution terms.
- Confirm no private absolute paths appear in manifests, reports, notebooks, or logs.
- Confirm related-work citations are current.
- Create a release tag and archive DOI only after the repository contents are stable.
