# Data Card

## Provenance

The dataset used in this sprint is intentionally synthetic or benchmark-derived and is meant for local evaluation only. It should not be treated as a production legal dataset.

## Quality

- Source quality is acceptable for baseline validation and demo workflows.
- Text normalization reduces formatting noise but does not guarantee legal precision.
- Clause examples may be simplified for early-stage model development.

## Limitations

- Templates are not representative of all contract styles.
- Entities and clause labels may be incomplete for real-world clauses.
- Matching and OCR extraction can vary by document structure and scan quality.

## Retention Policy

- Store canonical source files under the project-controlled `data/` tree.
- Keep generated artifacts for the active sprint only unless otherwise approved.
- Remove or sanitize any private or sensitive documents before final storage.
