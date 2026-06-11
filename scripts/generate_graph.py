import glob
import os
import time

import matplotlib.pyplot as plt
import pandas as pd

# Artifact structure: read run summaries from artifacts/runs/, write graphs to artifacts/reports/
RUNS_GLOB = os.path.join("artifacts", "runs", "*", "summary.csv")
REPORTS_DIR = os.path.join("artifacts", "reports")

# ==========================================
# 1. FIND AND LOAD ALL CSV FILES
# ==========================================
csv_files = glob.glob(RUNS_GLOB)

if not csv_files:
    print(f"Error: No run summaries found at '{RUNS_GLOB}'.")
    print("Run 'python run_benchmarks.py' first to generate benchmark data.")
    exit()

print(f"Found {len(csv_files)} benchmark runs. Processing data...")

# Create a timestamped folder for this report's graphs
report_dir = os.path.join(REPORTS_DIR, time.strftime("%Y%m%d_%H%M%S"))
os.makedirs(report_dir, exist_ok=True)
print(f"Saving graphs to: {report_dir}")

all_times = []
rows_x = None

for file in csv_files:
    df = pd.read_csv(file)
    if rows_x is None:
        rows_x = df["Rows"].tolist()
    all_times.append(df["Time (s)"].tolist())

# ==========================================
# 2. CALCULATE AVERAGES AND ETFs
# ==========================================
num_runs = len(all_times)
avg_times = [sum(times) / num_runs for times in zip(*all_times, strict=True)]

# --- NEW: Calculate ETF for 1,000,000 rows ---
TARGET_ROWS = 1_000_000
etf_hours_per_run = []

for times in all_times:
    # Use the largest N (1000 rows) to find the most accurate rate
    rate = times[-1] / rows_x[-1]
    etf_hours = (rate * TARGET_ROWS) / 3600
    etf_hours_per_run.append(etf_hours)

# Calculate the ETF based on the Average run
avg_rate = avg_times[-1] / rows_x[-1]
avg_etf_hours = (avg_rate * TARGET_ROWS) / 3600

# ==========================================
# GRAPH 1: ALL RUNS LAYERED
# ==========================================
plt.figure(figsize=(10, 6))
for i, times in enumerate(all_times):
    plt.plot(rows_x, times, marker="o", linestyle="-", alpha=0.5, label=f"Run {i + 1}")

plt.title(f"Translation Benchmarks: All {num_runs} Runs Layered", fontsize=14, fontweight="bold")
plt.xlabel("Number of Rows Processed", fontsize=12)
plt.ylabel("Time Taken in Seconds", fontsize=12)
plt.grid(True, linestyle=":", alpha=0.7)
if num_runs <= 10:
    plt.legend(fontsize=10)

layered_path = os.path.join(report_dir, "graph_layered_runs.png")
plt.savefig(layered_path, dpi=300, bbox_inches="tight")
print(f">>> Saved '{layered_path}'")
plt.close()

# ==========================================
# GRAPH 2: JUST THE AVERAGE
# ==========================================
plt.figure(figsize=(10, 6))
plt.plot(
    rows_x,
    avg_times,
    marker="D",
    linestyle="-",
    color="navy",
    linewidth=2.5,
    label=f"{num_runs}-Run Average",
)

plt.title(f"Translation Benchmarks: Average of {num_runs} Runs", fontsize=14, fontweight="bold")
plt.xlabel("Number of Rows Processed", fontsize=12)
plt.ylabel("Time Taken in Seconds", fontsize=12)
plt.legend(fontsize=11)
plt.grid(True, linestyle=":", alpha=0.7)

for i, txt in enumerate(avg_times):
    plt.annotate(
        f"{txt:.2f}s",
        (rows_x[i], avg_times[i]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        fontsize=9,
    )

average_path = os.path.join(report_dir, "graph_average_only.png")
plt.savefig(average_path, dpi=300, bbox_inches="tight")
print(f">>> Saved '{average_path}'")
plt.close()

# ==========================================
# GRAPH 3: ETF BAR CHART (1 MILLION ROWS)
# ==========================================
plt.figure(figsize=(10, 6))

# Setup the labels (Run 1, Run 2... Average)
bar_labels = [f"Run {i + 1}" for i in range(num_runs)] + ["AVERAGE"]
bar_values = etf_hours_per_run + [avg_etf_hours]

# Make the individual runs light blue, and the Average dark blue so it stands out
bar_colors = ["skyblue"] * num_runs + ["navy"]

bars = plt.bar(bar_labels, bar_values, color=bar_colors, edgecolor="black", alpha=0.8)

plt.title(
    f"Estimated Time to Finish (ETF) for {TARGET_ROWS:,} Rows", fontsize=14, fontweight="bold"
)
plt.ylabel("Estimated Time (Hours)", fontsize=12)
plt.grid(axis="y", linestyle=":", alpha=0.7)

# Add the exact hour numbers on top of the bars
for bar in bars:
    yval = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        yval + 0.15,
        f"{yval:.2f}h",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

etf_path = os.path.join(report_dir, "graph_etf_projection.png")
plt.savefig(etf_path, dpi=300, bbox_inches="tight")
print(f">>> Saved '{etf_path}'")
plt.close()

# ==========================================
# GRAPH 4: ETF STABILIZATION CURVE
# ==========================================
plt.figure(figsize=(10, 6))

TARGET_ROWS = 1_000_000

# Plot the stabilization curve for each run
for i, times in enumerate(all_times):
    # Calculate what the ETF for 1M rows would be AT EACH stage (10, 50, 100...)
    etf_progression = [
        ((time / row) * TARGET_ROWS) / 3600 for row, time in zip(rows_x, times, strict=True)
    ]
    plt.plot(rows_x, etf_progression, marker="o", linestyle="-", alpha=0.5, label=f"Run {i + 1}")

# Calculate and plot the average stabilization curve
avg_etf_progression = [
    ((time / row) * TARGET_ROWS) / 3600 for row, time in zip(rows_x, avg_times, strict=True)
]
plt.plot(
    rows_x,
    avg_etf_progression,
    marker="D",
    linestyle="-",
    color="navy",
    linewidth=2.5,
    label="Average Progression",
)

plt.title(f"ETF Stabilization Curve for {TARGET_ROWS:,} Rows", fontsize=14, fontweight="bold")
plt.xlabel("Number of Rows Processed in Benchmark", fontsize=12)
plt.ylabel("Projected Completion Time (Hours)", fontsize=12)
plt.grid(True, linestyle=":", alpha=0.7)

if num_runs <= 10:
    plt.legend(fontsize=10)

# Zoom in slightly by limiting the Y-axis, otherwise the massive 10-row estimate ruins the scale
plt.ylim(0, max(avg_etf_progression[1:]) * 1.5)

stabilization_path = os.path.join(report_dir, "graph_etf_stabilization.png")
plt.savefig(stabilization_path, dpi=300, bbox_inches="tight")
print(f">>> Saved '{stabilization_path}'")
plt.close()

# ==========================================
# GRAPH 5: PROCESSING RATE (RUNTIME / N)
# ==========================================
plt.figure(figsize=(10, 6))

# Plot the Rate (Time / Rows) for each run
for i, times in enumerate(all_times):
    rates = [time / row for time, row in zip(times, rows_x, strict=True)]
    plt.plot(rows_x, rates, marker="o", linestyle="-", alpha=0.4, label=f"Run {i + 1}")

# Calculate and plot the Average Rate
avg_rates = [time / row for time, row in zip(avg_times, rows_x, strict=True)]
plt.plot(
    rows_x,
    avg_rates,
    marker="D",
    linestyle="-",
    color="crimson",
    linewidth=2.5,
    label="Average Rate",
)

plt.title("Processing Rate vs. Batch Size (Runtime / N)", fontsize=14, fontweight="bold")
plt.xlabel("Number of Rows Processed (N)", fontsize=12)
plt.ylabel("Processing Rate (Seconds per Row)", fontsize=12)
plt.grid(True, linestyle=":", alpha=0.7)

if num_runs <= 10:
    plt.legend(fontsize=10)

# Add data labels to the average line so you can see exactly how fast it gets
for i, txt in enumerate(avg_rates):
    # Only label a few key points so it isn't cluttered
    if i == 0 or i == 2 or i == len(avg_rates) - 1:
        plt.annotate(
            f"{txt:.3f}s/row",
            (rows_x[i], avg_rates[i]),
            textcoords="offset points",
            xytext=(15, 10),
            ha="left",
            fontsize=9,
        )

rate_path = os.path.join(report_dir, "graph_processing_rate.png")
plt.savefig(rate_path, dpi=300, bbox_inches="tight")
print(f">>> Saved '{rate_path}'")
plt.close()

print(f"\nDone! Check '{report_dir}' for the images.")
