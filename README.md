# Run Locust tests (GitHub Action)

This repository provides a composite GitHub Action to run [Locust] load tests in CI/CD, with optional pass/fail thresholds and automatic artifact uploads (HTML + CSV reports). It is built to address the proposal in the Locust issue: [Official GitHub Action for running Locust tests #3233](https://github.com/locustio/locust/issues/3233).

## Features

- Headless Locust execution with `--csv` and optional HTML report
- Threshold checks: fail ratio, average response time, p95 response time
- Upload reports as workflow artifacts
- Flexible configuration (users, spawn rate, run time, tags, extra args)
- Optional additional Python requirements before running

## Usage

Add a workflow like this to `.github/workflows/locust.yml`:

```yaml
name: Locust
on:
  push:
  pull_request:

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Locust
        uses: ./. # or locustio/run-locust-action@v1 once published
        with:
          locust_file: tests/locustfile.py
          host: https://your-app.example.com
          users: 50
          spawn_rate: 10
          run_time: 2m
          check_fail_ratio: 0.02
          check_avg_response_time: 500
          check_p95_response_time: 1000
          upload_artifacts: true
```

Tip: This action uses bash in its internal steps. We recommend running on `ubuntu-latest`.

## Inputs

- `locust_file` (required): Path to your `locustfile.py`.
- `host` (required): Target host, for example `https://example.com`.
- `users`: Number of simulated users (`-u`).
- `spawn_rate`: Users spawned per second (`-r`).
- `run_time`: Test duration, e.g. `30s`, `2m`.
- `headless`: Run Locust headless (default `true`).
- `tags`: Run only tasks with any of these tags (comma-separated).
- `exclude_tags`: Exclude tasks with any of these tags (comma-separated).
- `log_level`: Locust log level (default `INFO`).
- `additional_args`: Extra arguments appended to the Locust command.
- `check_fail_ratio`: Max allowed failure ratio (0-1).
- `check_avg_response_time`: Max allowed average response time (ms).
- `check_p95_response_time`: Max allowed 95th percentile response time (ms).
- `python_version`: Python version (default `3.11`).
- `locust_version`: Locust version specifier (e.g. `2.29.1`, `~=2.29`).
- `requirements`: Optional `requirements.txt` to install before running.
- `output_dir`: Directory to place reports (default `locust-report`).
- `csv_prefix`: CSV filename prefix (default `locust_stats`).
- `html_report`: Generate HTML report (default `true`).
- `upload_artifacts`: Upload CSV/HTML as artifacts (default `true`).
- `artifact_name`: Artifact name (default `locust-report`).

## Caching and versions

- pip cache: Enabled automatically via setup-python only when a dependency file is present: `with.requirements`, `requirements.txt`, or `pyproject.toml`. In that case, Locust and other packages are installed using the pip cache. If no dependency file is found, pip cache is not enabled.
- To benefit from caching without an existing dependency file, either pass `requirements` pointing to a file, or create a minimal `requirements.txt` (for example: `locust==2.42.1`) and reference it via `with: requirements: requirements.txt`.
- Locust version: Pin via `locust_version`. Supports exact pins and operators (`==`, `~=`, `<`, `>`, `=`, `!`, `~`). If not provided, the latest Locust will be installed. If your requirements also pin Locust, `locust_version` (when set) takes precedence because Locust is installed after requirements.
- Python version: Set via `python_version` (default `3.11`).

## Outputs

- `fail_ratio`: Aggregated failure ratio.
- `avg_response_time`: Aggregated average response time (ms).
- `p95_response_time`: Aggregated 95th percentile response time (ms).
- `total_requests`: Total requests.
- `total_failures`: Total failures.
- `thresholds_passed`: `true`/`false` after applying checks.

## Example repository layout

This repo includes an example at `examples/basic/locustfile.py` compatible with `https://httpbin.org`. The CI workflow `.github/workflows/ci.yml` uses a local simple HTTP server and self-tests the action with:

- A passing run (thresholds generous)
- An expected failing run (enforces `check_fail_ratio: 0.0`)

## How it works

The action:

1. Sets up Python, installs your `requirements` (if provided), then installs Locust (honoring `locust_version` when set).
2. Runs Locust headless with `--csv` (and `--html` if enabled) into `output_dir`.
3. Parses the generated `<csv_prefix>_stats.csv` via `src/parse_stats.py` (using the `Aggregated` row) and derives:
   - Failure ratio (failures/requests)
   - Average response time (from `Aggregated`)
   - P95 (from `Aggregated`)
4. Enforces configured thresholds and sets step outputs. If thresholds are violated, the step fails.
5. Optionally uploads the HTML/CSV artifacts.

## License

MIT

[Locust]: https://locust.io