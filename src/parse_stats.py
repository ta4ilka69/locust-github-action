#!/usr/bin/env python3
import argparse
import csv
import os
import sys
from typing import List, Dict, Tuple, Optional


def read_stats_csv(csv_path: str) -> List[Dict[str, str]]:
    if not os.path.exists(csv_path):
        # CSV not found — return empty data and let callers get zeros.
        print(f"Stats CSV not found (defaulting to zeros): {csv_path}")
        return []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    return rows


def safe_int(value: Optional[str]) -> int:
    try:
        return int(value) if value is not None else 0
    except Exception:
        try:
            return int(float(value)) if value is not None else 0
        except Exception:
            return 0


def safe_float(value: Optional[str]) -> float:
    try:
        return float(value) if value is not None else float("nan")
    except Exception:
        return float("nan")


def normalize_key(key: str) -> str:
    return "".join(ch for ch in key.lower() if ch.isalnum())


def get_value(row: Dict[str, str], candidates: List[str]) -> Optional[str]:
    if not row:
        return None
    norm_map = {normalize_key(k): v for k, v in row.items()}
    for cand in candidates:
        v = norm_map.get(normalize_key(cand))
        if v is not None and v != "":
            return v
    return None


def aggregate_metrics(rows: List[Dict[str, str]]) -> Tuple[float, float, float, int, int]:
    agg_requests = 0
    agg_failures = 0
    agg_avg_rt = 0.0
    agg_p95 = 0.0

    found_agg = False
    for row in rows:
        if not row:
            continue
        name = (get_value(row, ["Name", "name"]) or "").strip().lower()
        if name == "aggregated":
            found_agg = True
            agg_requests = safe_int(
                get_value(
                    row,
                    [
                        "Requests",
                        "# requests",
                        "# reqs",
                        "reqs",
                        "num_requests",
                        "requests",
                        "Request Count",
                        "Total Requests",
                    ],
                )
            )
            agg_failures = safe_int(
                get_value(
                    row,
                    [
                        "Failures",
                        "# failures",
                        "# fails",
                        "fails",
                        "num_failures",
                        "failures",
                    ],
                )
            )
            agg_avg_rt = safe_float(
                get_value(
                    row,
                    [
                        "Average response time",
                        "Average Response Time",
                        "avg_response_time",
                        "AverageResponseTime",
                    ],
                )
            ) or 0.0
            agg_p95 = safe_float(
                get_value(
                    row,
                    [
                        "95%",
                        "95th percentile",
                        "p95",
                    ],
                )
            ) or 0.0
            break

    total_requests = agg_requests if found_agg else 0
    total_failures = agg_failures if found_agg else 0
    fail_ratio = (total_failures /
                  total_requests) if total_requests > 0 else 0.0
    avg_response_time = agg_avg_rt if found_agg else 0.0
    p95_response_time = agg_p95 if found_agg else 0.0
    return fail_ratio, avg_response_time, p95_response_time, total_requests, total_failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Parse Locust CSV stats and emit summary metrics"
    )
    parser.add_argument(
        "--csv-path",
        required=True,
        help="Path to *_stats.csv produced by Locust --csv",
    )
    parser.add_argument(
        "--github-output",
        required=False,
        help="Path to GITHUB_OUTPUT file to write outputs",
    )
    args = parser.parse_args()

    rows = read_stats_csv(args.csv_path)
    fail_ratio, avg_rt, p95_rt, total_requests, total_failures = aggregate_metrics(
        rows)

    # Export outputs
    outputs = {
        "fail_ratio": f"{fail_ratio:.6f}",
        "avg_response_time": f"{avg_rt:.2f}",
        "p95_response_time": f"{p95_rt:.2f}",
        "total_requests": str(total_requests),
        "total_failures": str(total_failures),
    }

    github_output_path = args.github_output or os.environ.get("GITHUB_OUTPUT")
    if github_output_path:
        with open(github_output_path, "a", encoding="utf-8") as f:
            for k, v in outputs.items():
                f.write(f"{k}={v}\n")

    print("Locust summary:")
    print(f"  total_requests: {total_requests}")
    print(f"  total_failures: {total_failures}")
    print(f"  fail_ratio: {fail_ratio:.6f}")
    print(f"  avg_response_time: {avg_rt:.2f} ms")
    print(f"  p95_response_time: {p95_rt:.2f} ms")

    return 0


if __name__ == "__main__":
    sys.exit(main())
