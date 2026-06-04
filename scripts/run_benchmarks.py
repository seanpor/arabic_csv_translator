import json
import os
import platform
import subprocess
import sys
import time

import pandas as pd

# Artifact output structure: each run's data lands under artifacts/runs/<timestamp>/
ARTIFACTS_DIR = "artifacts"
RUNS_DIR = os.path.join(ARTIFACTS_DIR, "runs")


def get_git_revision():
    """Returns the short git commit hash, or 'unknown' if unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def create_benchmark_input(source_csv, target_csv, num_rows):
    """Creates a temporary benchmark file by extracting rows from the source data."""
    print(f"Preparing {num_rows}-line input from {source_csv} -> {target_csv}...")
    try:
        # read_csv with nrows is highly efficient; it stops reading after num_rows
        df = pd.read_csv(source_csv, nrows=num_rows)
        df.to_csv(target_csv, index=False)
        return True
    except FileNotFoundError:
        print(
            f"Error: Source file '{source_csv}' not found. "
            "Make sure it is in your current directory."
        )
        return False
    except Exception as e:
        print(f"Error creating benchmark file: {e}")
        return False


def run_benchmark(filename):
    output = "results_" + filename
    print(f"\n>>> Benchmarking {filename}...")
    start_time = time.time()

    result = subprocess.run(
        [sys.executable, "main.py", "--input", filename, "--output", output, "--no-resume"],
        capture_output=True,
        text=True,
    )

    end_time = time.time()
    duration = end_time - start_time

    if result.returncode != 0:
        print(f"Error during benchmark: {result.stderr}")
        return None

    # Get row count from file name or by reading it
    rows = len(pd.read_csv(filename))

    avg_per_row = duration / rows
    rows_per_hour = 3600 / avg_per_row

    print(f"Completed {rows} rows in {duration:.2f} seconds.")
    print(f"Average: {avg_per_row:.4f} seconds/row")
    print(f"Estimated throughput: {rows_per_hour:.0f} rows/hour")

    # Cleanup
    if os.path.exists(output):
        os.remove(output)
    if os.path.exists(output + ".checkpoint"):
        os.remove(output + ".checkpoint")

    return {"rows": rows, "duration": duration, "avg": avg_per_row, "per_hour": rows_per_hour}


if __name__ == "__main__":
    SOURCE_DATA = "data.csv"

    # Define the sizes you want to benchmark.
    benchmark_sizes = [10, 50, 100, 500, 1000]

    results = []
    generated_files = []

    print("Generating Benchmark Files")
    for size in benchmark_sizes:
        filename = f"benchmark_{size}.csv"
        # Generate the files dynamically right before we run them
        if create_benchmark_input(SOURCE_DATA, filename, size):
            generated_files.append(filename)
        else:
            print("Aborting benchmarks due to file creation error.")
            sys.exit(1)

    print("\nRunning Benchmarks")
    for f in generated_files:
        if os.path.exists(f):
            res = run_benchmark(f)
            if res:
                results.append(res)

    print("\n" + "=" * 40)
    print("FINAL BENCHMARK SUMMARY")
    print("=" * 40)
    print(f"{'Rows':<10} | {'Time (s)':<10} | {'Rows/hr':<10}")
    print("-" * 40)
    for r in results:
        print(f"{r['rows']:<10} | {r['duration']:<10.2f} | {r['per_hour']:<10.0f}")

    if results:
        total_1m_hours = (1_000_000 * results[-1]["avg"]) / 3600
        print(f"\nEstimated time for 1,000,000 rows: {total_1m_hours:.1f} hours")

        # 1. Generate a unique timestamp (YearMonthDay_HourMinuteSecond)
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # 2. Create this run's artifact folder: artifacts/runs/<timestamp>/
        run_dir = os.path.join(RUNS_DIR, timestamp)
        os.makedirs(run_dir, exist_ok=True)

        # 3. Convert results into a Pandas DataFrame and rename columns for readability
        df_summary = pd.DataFrame(results)
        df_summary = df_summary.rename(
            columns={
                "rows": "Rows",
                "duration": "Time (s)",
                "avg": "Average Time/Row (s)",
                "per_hour": "Estimated Rows/hr",
            }
        )

        # 4. Save the summary table inside this run's folder
        summary_path = os.path.join(run_dir, "summary.csv")
        df_summary.to_csv(summary_path, index=False)
        print(f"\n>>> Saved summary table to: {summary_path}")

        # 5. Save run provenance so runs can be told apart when aggregated later
        meta = {
            "timestamp": timestamp,
            "source_data": SOURCE_DATA,
            "benchmark_sizes": benchmark_sizes,
            "git_revision": get_git_revision(),
            "host": platform.node(),
            "python_version": platform.python_version(),
            "estimated_1m_hours": round(total_1m_hours, 2),
        }
        meta_path = os.path.join(run_dir, "meta.json")
        with open(meta_path, "w") as f:
            json.dump(meta, f, indent=2)
        print(f">>> Saved run metadata to: {meta_path}")

    # Cleanup the generated input files
    print("\nCleaning up temporary files")
    for f in generated_files:
        if os.path.exists(f):
            os.remove(f)
    print("Done.")