#!/usr/bin/env bash
# benchmark_50.sh
# Takes rows 1-50 from data.csv (raw, untranslated) as temp input and runs main.py on them.
# No project files are modified. Temp file lives in /tmp and is cleaned up after.

set -euo pipefail

DATA="data.csv"
TEMP_INPUT="/tmp/benchmark_input_50.csv"
TEMP_OUTPUT="/tmp/benchmark_output_50.csv"
FINAL_OUTPUT="benchmark_results_50.csv"
PYTHON="./venv/bin/python"

echo "[benchmark_50] Preparing 50-line temp input from rows 1-50 of ${DATA}..."

# Write header + first 50 data rows from raw source
{ head -1 "${DATA}"; \
  sed '1d' "${DATA}" | tail -50; \
} > "${TEMP_INPUT}"

LINE_COUNT=$(wc -l < "${TEMP_INPUT}")
echo "[benchmark_50] Temp input ready: ${LINE_COUNT} lines (header + 50 rows) at ${TEMP_INPUT}"

echo "[benchmark_50] Starting translation benchmark..."
START_TIME=$(date +%s)

"${PYTHON}" main.py --input "${TEMP_INPUT}" --output "${TEMP_OUTPUT}" --no-resume

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "[benchmark_50] Finished in ${ELAPSED} seconds."

# Move result to project directory for inspection
mv "${TEMP_OUTPUT}" "${FINAL_OUTPUT}"
echo "[benchmark_50] Results saved to ${FINAL_OUTPUT}"

# Cleanup temp input
rm -f "${TEMP_INPUT}"
echo "[benchmark_50] Temp input cleaned up."

# Quick summary
echo ""
echo "--- Benchmark Summary ---"
echo "Rows processed : 50"
echo "Elapsed time   : ${ELAPSED}s"
SUCCESS_COUNT=$(tail -n +2 "${FINAL_OUTPUT}" | cut -d',' -f4 | grep -c "SUCCESS" || true)
ERROR_COUNT=$(tail -n +2 "${FINAL_OUTPUT}" | cut -d',' -f4 | grep -c "ERROR" || true)
echo "Successes      : ${SUCCESS_COUNT}"
echo "Errors         : ${ERROR_COUNT}"
echo "-------------------------"
