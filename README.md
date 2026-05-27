# Arabic to English Offline Translator 🌍

[![Python tests](https://github.com/seanpor/arabic_csv_translator/actions/workflows/test.yml/badge.svg)](https://github.com/seanpor/arabic_csv_translator/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance, robust, and entirely offline framework for translating large-scale Arabic document metadata to English. Powered by Meta's **NLLB-200** model.

## Key Features
- **Batched Inference:** Optimized for multi-core CPUs/GPUs, processing up to 20,000 rows/hour.
- **Fault Tolerant:** Automatic state checkpointing allows resuming 1M+ row batches after any interruption.
- **Data Integrity:** Preserves original CSV structure and document IDs.
- **Containerized:** Docker support for instant, zero-config deployment.
- **Professional CLI:** Featuring `tqdm` progress tracking and formal logging.

---

## 💻 Prerequisites

### For macOS Users
To run this tool on a Mac without affecting your system settings, you need **one** of the following:
1.  **Docker Desktop** (Recommended): The easiest way to run everything in a clean container.
2.  **Homebrew Python**: If running natively, we recommend using Homebrew to install Python 3.11 (`brew install python@3.11`).

### For Linux Users
- **Python 3.8+** and `python3-venv`
- **Docker** (optional, for containerized runs)

---

## 🚀 Installation & Usage

### Option A: Docker (Professional & Isolated)
*Best for: Users who don't want to manage Python environments.*

1.  **Build the image** (Bakes the 2.4GB model inside):
    ```bash
    docker build -t arabic-translator .
    ```
2.  **Run the translator**: 
    ```bash
    docker run -v $(pwd):/data arabic-translator --input /data/input.csv --output /data/results.csv
    ```

### Option B: Native Setup (Isolated Virtual Environment)
*Best for: Developers who want to run or test the code directly.*

1.  **Create an isolated environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On macOS/Linux
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Download the model** (Required once):
    ```bash
    python scripts/download_model.py
    ```
4.  **Run**:
    ```bash
    python main.py --input data.csv --output results.csv
    ```

---

## 🛡 Environment Safety
This project is designed to be **environment-safe**:
- **Docker path:** Zero installation on the host machine. Everything stays inside the container.
- **Native path:** Uses `venv` to ensure no global Python packages are ever modified.

---

## 🛠 Configuration
Adjust settings in `config.py` to match your hardware and dataset.

### Supporting Other Languages
While this tool is pre-configured for **Arabic to English**, the underlying NLLB-200 model supports over **200 languages**. You can change the language pair in `config.py` using the **FLORES-200** codes.

- **Source:** `SRC_LANG`
- **Target:** `TGT_LANG`
- **Full list of supported language codes:** [FLORES-200 Language List](https://github.com/facebookresearch/flores/blob/main/flores200/README.md#languages-in-flores-200)

### Hardware Optimization
- `INFERENCE_BATCH_SIZE`: Set to 8-16 for CPU, 32-64 for GPU.
- `CHECKPOINT_BATCH_SIZE`: Frequency of disk persistence.

---

## 📊 Performance Projections (CPU)
| Dataset Size | Estimated Time |
| :--- | :--- |
| 1,000 rows | 3 minutes |
| 10,000 rows | 30 minutes |
| 1,000,000 rows | 50 hours (approx. 2 days) |

*Note: Performance on GPU is typically 5-10x faster.*

---

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Documentation
Additional resources and formal documentation:
- **[Technical Report](docs/technical_report.pdf):** Academic-style overview of system architecture and benchmarks.
- **[Project Plan](docs/PLAN.md):** Detailed implementation milestones.
- **[Phase Plans](docs/phases/):** Specific design documents for project upgrades.
