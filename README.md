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
          locust-file: tests/locustfile.py
          host: https://your-app.example.com
          users: 50
          spawn-rate: 10
          run-time: 2m
          check-fail-ratio: 0.02
          check-avg-response-time: 500
          check-p95-response-time: 1000
          upload-artifacts: true
```

Tip: This action uses bash in its internal steps. We recommend running on `ubuntu-latest`.

## Inputs

- `locust-file` (required): Path to your `locustfile.py`.
- `host` (required): Target host, for example `https://example.com`.
- `users`: Number of simulated users (`-u`).
- `spawn-rate`: Users spawned per second (`-r`).
- `run-time`: Test duration, e.g. `30s`, `2m`.
- `headless`: Run Locust headless (default `true`).
- `tags`: Run only tasks with any of these tags (comma-separated).
- `exclude-tags`: Exclude tasks with any of these tags (comma-separated).
- `log-level`: Locust log level (default `INFO`).
- `additional-args`: Extra arguments appended to the Locust command.
- `check-fail-ratio`: Max allowed failure ratio (0-1).
- `check-avg-response-time`: Max allowed average response time (ms).
- `check-p95-response-time`: Max allowed 95th percentile response time (ms).
- `python-version`: Python version (default `3.11`).
- `locust-version`: Locust version specifier (e.g. `2.29.1`, `~=2.29`).
- `requirements`: Optional `requirements.txt` to install before running.
- `output-dir`: Directory to place reports (default `locust-report`).
- `csv-prefix`: CSV filename prefix (default `locust_stats`).
- `html-report`: Generate HTML report (default `true`).
- `upload-artifacts`: Upload CSV/HTML as artifacts (default `true`).
- `artifact-name`: Artifact name (default `locust-report`).

## Outputs

- `fail_ratio`: Aggregated failure ratio.
- `avg_response_time`: Aggregated average response time (ms).
- `p95_response_time`: Aggregated 95th percentile response time (ms).
- `total_requests`: Total requests.
- `total_failures`: Total failures.
- `thresholds_passed`: `true`/`false` after applying checks.

## Example repository layout

This repo includes an example at `examples/basic/locustfile.py` using `https://httpbin.org`. The CI workflow `.github/workflows/ci.yml` self-tests the action with:

- A passing run (thresholds generous)
- An expected failing run (enforces `check-fail-ratio: 0.0`)

## How it works

The action:

1. Sets up Python and installs Locust (optionally your `requirements.txt`).
2. Runs Locust headless with `--csv` (and `--html` if enabled) into `output-dir`.
3. Parses the generated `<csv-prefix>_stats.csv` via `src/parse_stats.py` to compute:
   - Failure ratio
   - Weighted average response time
   - Conservative global p95 (max of per-endpoint p95)
4. Enforces configured thresholds and sets step outputs. If thresholds are violated, the step fails.
5. Optionally uploads the HTML/CSV artifacts.

## Contributing / Roadmap

Planned improvements:

- Additional threshold types (RPS, median, per-endpoint thresholds)
- Windows/macOS runner support guidance and tests
- Richer summary annotations in job logs

We intend to upstream this to the official Locust org pending feedback on [the proposal](https://github.com/locustio/locust/issues/3233).

## License

MIT

[Locust]: https://locust.io