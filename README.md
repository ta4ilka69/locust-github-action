# Run Locust tests (GitHub Action)

This repository provides a composite GitHub Action to run [Locust] load tests in CI/CD with minimal coupling to Locust CLI. It passes through your arguments to Locust, produces CSV/HTML reports, uploads them as artifacts, and exposes summary metrics as outputs. It is built to address the proposal in the Locust issue: [Official GitHub Action for running Locust tests #3233](https://github.com/locustio/locust/issues/3233).

## Features

- Headless Locust execution with `--csv` (and optional `--html`)
- Pass-through CLI args to stay compatible with Locust changes (`with.args`)
- Upload HTML/CSV reports as workflow artifacts
- Expose summary metrics (fail ratio, avg, p95, totals) as outputs

## Usage

Add a workflow like this to `.github/workflows/locust.yml` (install Python/Locust in your workflow, then call the action):

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
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install locust

      - name: Run Locust
        uses: ./. # or locustio/run-locust-action@v1 once published
        with:
          locust_file: tests/locustfile.py
          args: --host https://your-app.example.com -u 50 -r 10 -t 2m
          csv_base: locust-report/locust_stats
          html_report: true
          upload_artifacts: true
```

Tip: This action uses bash in its internal steps. We recommend running on `ubuntu-latest`.

## Inputs

- `locust_file`: Path to your `locustfile.py` (optional; Locust auto-discovers if omitted).
- `args`: Raw CLI arguments appended to the Locust command (preferred way to configure Locust).
- `config_file`: Optional path to Locust config file, passed with `--config`.
- `csv_base`: Base path for reports, e.g. `locust-report/locust_stats` (default).
- `html_report`: Generate HTML report (default `true`).
- `upload_artifacts`: Upload CSV/HTML as artifacts (default `true`).
- `artifact_name`: Artifact name (default `locust-report`).

## Caching and versions

Use standard actions to prepare Python and dependencies (this action does not install Python or Locust):

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: pip
    cache-dependency-path: requirements.txt
- run: pip install -r requirements.txt  # or: pip install locust==2.42.1
```

## Outputs

- `fail_ratio`: Aggregated failure ratio.
- `avg_response_time`: Aggregated average response time (ms).
- `p95_response_time`: Aggregated 95th percentile response time (ms).
- `total_requests`: Total requests.
- `total_failures`: Total failures.

## Example repository layout

This repo includes an example at `examples/basic/locustfile.py` compatible with `https://httpbin.org`. The CI workflow `.github/workflows/ci.yml` uses a local simple HTTP server and self-tests the action with:

- A passing run
- Negative runs (missing host / missing locustfile)
- Tag include/exclude examples
- Version pin + pip cache example

## Recommended Python setup

We recommend setting up Python in your workflow before invoking this action, for maximum control and flexibility:

```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.12'
    cache: pip
    cache-dependency-path: requirements.txt
```

Then call this action:

```yaml
- name: Run Locust (pass-through args)
  uses: ./. # or locustio/run-locust-action@v1
  with:
    locust_file: examples/basic/locustfile.py
    args: --host http://127.0.0.1:8000 -u 5 -r 5 -t 10s --tags fast --loglevel INFO
    csv_base: locust-report/locust_stats
```

## How it works

The action:

1. Runs Locust headless with `--csv` (and `--html` if enabled), passing through your `args` and optional `config_file`.
2. Parses the generated `<csv_prefix>_stats.csv` via `src/parse_stats.py` (using the `Aggregated` row) and derives:
   - Failure ratio (failures/requests)
   - Average response time (from `Aggregated`)
   - P95 (from `Aggregated`)
3. Propagates Locust’s exit code. Threshold enforcement should be handled inside your Locust run (e.g., via plugins) or in separate steps/scripts.
4. Optionally uploads the HTML/CSV artifacts.

## License

MIT

[Locust]: https://locust.io