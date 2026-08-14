import argparse
import json
from pathlib import Path
from typing import Optional

from engine.ollama_client import OllamaABSAClient


DATA_PATH = Path("data/train_preprocess.txt")
OUTPUT_PATH = Path("data/processed_reviews.json")

ollama_client = OllamaABSAClient()


def load_terma_sentences(file_path: Path) -> list[str]:
    """
    Membaca dataset TERMA yang menyimpan token per baris
    dan merekonstruksi token menjadi kalimat/review.
    """

    sentences = []
    current_words = []

    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            # Baris kosong = akhir satu kalimat
            if not line:
                if current_words:
                    if len(current_words) >= 4:
                        sentences.append(
                            " ".join(current_words)
                        )

                    current_words = []

                continue

            parts = line.split()

            if parts:
                # Ambil token pertama.
                current_words.append(parts[0])

    # Handle kalimat terakhir
    if current_words and len(current_words) >= 4:
        sentences.append(
            " ".join(current_words)
        )

    return sentences


def process_batch(
    limit: Optional[int] = 15,
    data_path: Path = DATA_PATH,
    output_path: Path = OUTPUT_PATH,
) -> None:

    # ========================================================
    # VALIDASI DATASET
    # ========================================================

    if not data_path.exists():
        print(
            f"❌ File dataset tidak ditemukan: {data_path}\n"
            "Pastikan train_preprocess.txt berada di folder data/."
        )
        return

    # ========================================================
    # VALIDASI OLLAMA
    # ========================================================

    print("🔌 Mengecek koneksi Ollama...")

    if not ollama_client.is_available():
        print(
            "❌ Ollama tidak dapat diakses.\n"
            "Pastikan Ollama sedang berjalan."
        )
        return

    print("✅ Ollama tersedia.")

    if not ollama_client.model_exists():
        print(
            f"❌ Model '{ollama_client.model_name}' tidak ditemukan.\n"
            f"Jalankan:\n\n"
            f"    ollama pull {ollama_client.model_name}"
        )
        return

    print(
        f"✅ Model '{ollama_client.model_name}' tersedia.\n"
    )

    # ========================================================
    # LOAD DATASET
    # ========================================================

    reviews = load_terma_sentences(data_path)

    if not reviews:
        print(
            "⚠️ Tidak ada review yang berhasil "
            "direkonstruksi dari dataset."
        )
        return

    total_found = len(reviews)

    if limit is None:
        sample_reviews = reviews
    else:
        sample_reviews = reviews[:limit]

    print(
        f"📖 Total review berhasil direkonstruksi : "
        f"{total_found}"
    )

    print(
        f"🔄 Review yang akan dianalisis           : "
        f"{len(sample_reviews)}"
    )

    print(
        f"🤖 Model                                 : "
        f"{ollama_client.model_name}"
    )

    print("\n" + "=" * 60)

    # ========================================================
    # BATCH PROCESSING
    # ========================================================

    results = []

    success_count = 0
    empty_count = 0
    error_count = 0

    for idx, review_text in enumerate(
        sample_reviews,
        start=1,
    ):

        preview = review_text[:80]

        if len(review_text) > 80:
            preview += "..."

        print(
            f"[{idx}/{len(sample_reviews)}] "
            f"{preview}"
        )

        try:
            aspects = ollama_client.analyze_review(
                review_text
            )

            if aspects:
                status = "success"
                success_count += 1
            else:
                status = "empty"
                empty_count += 1

            results.append(
                {
                    "review_id": idx,
                    "review_text": review_text,
                    "aspects": aspects,
                    "status": status,
                    "error": None,
                }
            )

            print(
                f"   → {len(aspects)} aspek terdeteksi"
            )

        except Exception as exc:

            error_count += 1

            results.append(
                {
                    "review_id": idx,
                    "review_text": review_text,
                    "aspects": [],
                    "status": "error",
                    "error": str(exc),
                }
            )

            print(
                f"   ⚠️ Error: {exc}"
            )

    # ========================================================
    # SAVE OUTPUT
    # ========================================================

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            results,
            f,
            indent=2,
            ensure_ascii=False,
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print("✅ BATCH PROCESSING SELESAI")
    print("=" * 60)

    print(
        f"Total dataset       : {total_found}"
    )

    print(
        f"Total diproses      : {len(sample_reviews)}"
    )

    print(
        f"Berhasil            : {success_count}"
    )

    print(
        f"Tanpa aspek         : {empty_count}"
    )

    print(
        f"Error               : {error_count}"
    )

    print(
        f"Output              : {output_path}"
    )

    print("=" * 60)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Batch processing dataset TERMA "
            "menggunakan Qwen3:8B."
        )
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=15,
        help=(
            "Jumlah review yang diproses. "
            "Gunakan --limit 50 untuk testing."
        ),
    )

    args = parser.parse_args()

    process_batch(
        limit=args.limit
    )


if __name__ == "__main__":
    main()