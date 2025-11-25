#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8001}"

mkdir -p store-report
python examples/store/server.py > store-server.log 2>&1 &
SERVER_PID=$!
sleep 2

set +e
locust -f examples/store/locustfile.py \
  --headless \
  --host "http://127.0.0.1:${PORT}" \
  -u 5 -r 5 -t 10s \
  --csv store-report/stats \
  --html store-report/stats.html
STATUS=$?
set -e

kill "${SERVER_PID}" || true
wait "${SERVER_PID}" 2>/dev/null || true

echo "Locust exit code: ${STATUS}"
exit "${STATUS}"


