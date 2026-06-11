# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project aims to adhere to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Benchmarking harness** (`run_benchmarks.py`): builds inputs by slicing `data.csv`
  across a configurable list of sizes, times each through `main.py` with `--no-resume`,
  and saves results to a timestamped `artifacts/runs/<timestamp>/` folder containing a
  `summary.csv` and a `meta.json`.
- **Reporting script** (`generate_graph.py`): reads every `artifacts/runs/*/summary.csv`,
  averages the runs, and renders scaling and projection graphs into a timestamped
  `artifacts/reports/<timestamp>/` folder.
- **Per-run provenance** (`meta.json`): records git revision, host, benchmark sizes, and
  source file, so runs can be told apart when aggregated.
- `make setup` (bootstrap venv + tooling) and `make fix` (auto-format) targets.

### Changed
- Benchmark results are now **persisted as files** under `artifacts/`, instead of only
  being printed to the terminal.
- Benchmark inputs are now generated from real `data.csv` rows, instead of a fixed set
  of pre-made synthetic files.

### Notes
- Folders under `artifacts/` are created on demand by the scripts — no setup step needed.
- The translation engine (`main.py`, `src/`) is unchanged by this work.
