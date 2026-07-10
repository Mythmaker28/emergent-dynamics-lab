# Artifact Storage Policy

Small and moderate experiments commit full reproducible tables. Large screens may keep raw tables locally under `results/<experiment>/raw/`, which `.gitignore` excludes, when committing them would make Git unreasonable.

For every excluded raw file, commit:

- relative path and schema;
- byte size and SHA-256;
- experiment/code commit and complete manifest;
- exact command and deterministic inputs;
- row counts and aggregate consistency checks;
- summaries, plots, LawSpecs, candidate rows, and indexed derived tables.

Raw exclusion is a storage decision, not permission to discard provenance or report aggregates that cannot be regenerated.

