import argparse
import logging
import os
import sys

import pandas as pd
from tqdm import tqdm

from src import config
from src.translator import ArabicTranslator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("translation_session.log"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def get_checkpoint_path(output_path: str) -> str:
    """Generates the checkpoint file path for a given output path."""
    return output_path + config.CHECKPOINT_SUFFIX


def process_csv(input_path: str, output_path: str, resume: bool = True) -> None:
    """
    Orchestrates the batch translation of a CSV file using memory-efficient streaming.
    """
    checkpoint_path = get_checkpoint_path(output_path)

    # 1. Determine starting point for Resume
    start_index = 0
    if resume and os.path.exists(checkpoint_path):
        logger.info(f"Checkpoint detected at {checkpoint_path}. Attempting to resume...")
        try:
            # We count rows in the existing output that have a valid status
            df_check = pd.read_csv(checkpoint_path)
            if config.STATUS_COLUMN in df_check.columns:
                # Filter out rows where status is NaN
                df_valid = df_check.dropna(subset=[config.STATUS_COLUMN])
                start_index = len(df_valid)
                # Overwrite checkpoint with ONLY valid rows to ensure clean append
                df_valid.to_csv(checkpoint_path, index=False)
                logger.info(f"Resuming from row index {start_index}.")
        except Exception as e:
            logger.warning(f"Checkpoint unreadable: {e}. Starting from scratch.")

    # 2. Initialize Translator
    try:
        translator = ArabicTranslator()
    except Exception as e:
        logger.error(f"Fatal: Translator initialization failed: {e}")
        sys.exit(1)

    # 3. Processing Loop (Row-based for perfect resume accuracy)
    try:
        df_input = pd.read_csv(input_path)
        total_rows = len(df_input)

        # Open checkpoint file in append mode or write fresh
        if start_index == 0:
            # Create fresh file with header
            df_init = df_input.iloc[0:0].copy()
            df_init[config.TRANSLATED_COLUMN] = None
            df_init[config.STATUS_COLUMN] = None
            df_init[config.ERROR_COLUMN] = None
            df_init.to_csv(checkpoint_path, index=False)

        with tqdm(total=total_rows, initial=start_index, desc="Translating", unit="row") as pbar:
            for i in range(start_index, total_rows, config.INFERENCE_BATCH_SIZE):
                end_idx = min(i + config.INFERENCE_BATCH_SIZE, total_rows)
                batch = df_input.iloc[i:end_idx].copy()

                batch_texts = batch[config.TEXT_COLUMN].astype(str).tolist()
                batch_results = translator.translate_batch(batch_texts)

                results, statuses, errors = zip(*batch_results, strict=True)
                batch[config.TRANSLATED_COLUMN] = results
                batch[config.STATUS_COLUMN] = statuses
                batch[config.ERROR_COLUMN] = errors

                # Append to checkpoint immediately
                batch.to_csv(checkpoint_path, mode="a", index=False, header=False)
                pbar.update(len(batch))

    except KeyboardInterrupt:
        logger.info("\nSession interrupted. Progress is safe in the checkpoint file.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Processing error: {e}")
        raise

    # 4. Finalize
    logger.info(f"Moving final results to {output_path}")
    if os.path.exists(output_path):
        os.remove(output_path)
    os.rename(checkpoint_path, output_path)
    logger.info("Task finished successfully.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Professional Offline Arabic to English Translation Framework"
    )
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    parser.add_argument(
        "--no-resume",
        action="store_false",
        dest="resume",
        help="Disable auto-resume from checkpoint",
    )

    args = parser.parse_args()

    if not os.path.exists(config.MODEL_PATH):
        logger.error(f"Model assets not found at {config.MODEL_PATH}.")
        logger.info(
            "Run './venv/bin/python scripts/download_model.py' to download required model files."
        )
        sys.exit(1)

    process_csv(args.input, args.output, resume=args.resume)
