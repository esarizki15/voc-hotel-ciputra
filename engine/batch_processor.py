import argparse
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

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

        # Cek apakah dataset sudah punya kolom ID bawaan
        id_col = None
        for col in ["review_id", "id", "ID"]:
            if col in df.columns:
                id_col = col
                break

        for idx, row in df.reset_index(drop=True).iterrows():
            review_text = str(row[review_column]) if pd.notna(row[review_column]) else ""

            # Ambil ID asli dari Excel jika ada, jika tidak gunakan nomor urut idx + 1
            current_id = row[id_col] if id_col and pd.notna(row[id_col]) else idx + 1

            # Tinjau jika teks review kosong
            if not review_text.strip():
                results.append({
                    "review_id": current_id,
                    "review_text": "",
                    "aspects": [],
                    "status": "empty",
                    "error": "Teks review kosong",
                })
                if progress_callback:
                    progress_callback(idx + 1, total)
                continue

            try:
                aspects = self.ollama_client.analyze_review(review_text)
                # Analisis berhasil (walaupun aspeknya []), status tetap "success"
                status = "success"
                error = None
            except Exception as exc:
                aspects = []
                status = "error"
                error = str(exc)

            results.append({
                "review_id": current_id,
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