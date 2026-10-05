import argparse
import json
import random
from pathlib import Path

from engine.categories import CATEGORY_DESCRIPTIONS


def create_template(
    input_path: Path,
    output_path: Path,
    limit: int | None = 50,
    seed: int | None = None,
):
    if not input_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {input_path}")

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("processed_reviews.json harus berupa list.")

    if limit is not None:
        if seed is not None:
            # Sampel acak (reproducible) agar tidak hanya ulasan awal file
            data = random.Random(seed).sample(data, min(limit, len(data)))
        else:
            data = data[:limit]

    gold = []

    for item in data:
        if not isinstance(item, dict):
            continue

        gold.append(
            {
                "review_id": item.get("review_id"),
                "review_text": item.get("review_text", ""),
                "gold_aspects": [],
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(gold, f, ensure_ascii=False, indent=2)

    print(f"✅ Template gold label dibuat: {output_path}")
    print(f"📝 Total review untuk labeling: {len(gold)}")
    print()
    print("Isi gold_aspects secara manual berdasarkan review_text (tanpa melihat prediksi model).")
    print("Kategori yang valid:")
    for name, desc in CATEGORY_DESCRIPTIONS.items():
        print(f"  - {name}: {desc}")
    print("Contoh:")
    print("""
"gold_aspects": [
  {
    "category": "Kamar",
    "sentiment": "negatif"
  },
  {
    "category": "Wi-Fi",
    "sentiment": "negatif"
  }
]
""")


def main():
    parser = argparse.ArgumentParser(
        description="Membuat template gold label dari processed_reviews.json."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed_combined-reviews.json"),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/gold/gold_template.json"),  # di subfolder agar tidak muncul sebagai dataset dashboard
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Jumlah review yang dibuatkan template. Default: 50.",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed sampel acak. Gunakan -1 untuk mengambil N review pertama.",
    )

    args = parser.parse_args()

    create_template(
        input_path=args.input,
        output_path=args.output,
        limit=args.limit,
        seed=None if args.seed < 0 else args.seed,
    )


if __name__ == "__main__":
    main()