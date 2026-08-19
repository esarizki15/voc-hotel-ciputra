import argparse
import json
from pathlib import Path
from typing import Callable, List, Dict, Any, Optional

import pandas as pd
from engine.ollama_client import OllamaABSAClient

DATA_PATH = Path("data/train_preprocess.txt")
OUTPUT_PATH = Path("data/processed_reviews.json")


class BatchProcessor:
    def __init__(self, ollama_client: Optional[OllamaABSAClient] = None):
        self.ollama_client = ollama_client or OllamaABSAClient()

    def process_dataframe(
        self,
        df: pd.DataFrame,
        review_column: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> List[Dict[str, Any]]:

        results = []
        total = len(df)

        for idx, row in df.reset_index(drop=True).iterrows():
            review_text = str(row[review_column]) if pd.notna(row[review_column]) else ""

            if not review_text.strip():
                results.append({
                    "review_id": idx + 1,
                    "review_text": "",
                    "aspects": [],
                    "status": "empty",
                    "error": None,
                })
                if progress_callback:
                    progress_callback(idx + 1, total)
                continue

            try:
                aspects = self.ollama_client.analyze_review(review_text)
                status = "success" if aspects else "empty"
                error = None
            except Exception as exc:
                aspects = []
                status = "error"
                error = str(exc)

            results.append({
                "review_id": idx + 1,
                "review_text": review_text,
                "aspects": aspects,
                "status": status,
                "error": error,
            })

            if progress_callback:
                progress_callback(idx + 1, total)

        return results

    def save_results(self, results: List[Dict[str, Any]], output_path: Path | str) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)


# ========================================================
# UNTUK KEBUTUHAN RUN VIA CLI (Opsional)
# ========================================================

def load_terma_sentences(file_path: Path) -> list[str]:
    sentences = []
    current_words = []

    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_words and len(current_words) >= 4:
                    sentences.append(" ".join(current_words))
                current_words = []
                continue
            parts = line.split()
            if parts:
                current_words.append(parts[0])

    if current_words and len(current_words) >= 4:
        sentences.append(" ".join(current_words))

    return sentences


def process_batch(
    limit: Optional[int] = 15,
    data_path: Path = DATA_PATH,
    output_path: Path = OUTPUT_PATH,
) -> None:
    if not data_path.exists():
        print(f"❌ File dataset tidak ditemukan: {data_path}")
        return

    reviews = load_terma_sentences(data_path)
    if not reviews:
        return

    df = pd.DataFrame({"review_text": reviews[:limit] if limit else reviews})
    processor = BatchProcessor()
    
    print("🔄 Memproses batch...")
    results = processor.process_dataframe(df, review_column="review_text")
    processor.save_results(results, output_path)
    print(f"✅ Selesai. Disimpan di {output_path}")


if __name__ == "__main__":
    process_batch()