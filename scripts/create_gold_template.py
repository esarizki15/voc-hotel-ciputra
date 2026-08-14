import argparse
import json
from pathlib import Path


def create_template(
    input_path: Path,
    output_path: Path,
    limit: int | None = 50,
):
    if not input_path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {input_path}")

    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("processed_reviews.json harus berupa list.")

    if limit is not None:
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
    print("Isi gold_aspects secara manual berdasarkan review_text.")
    print("Contoh:")
    print("""
"gold_aspects": [
  {
    "category": "AC",
    "sentiment": "negatif"
  },
  {
    "category": "WiFi",
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
        default=Path("data/processed_reviews.json"),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/gold_reviews.json"),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Jumlah review yang dibuatkan template. Default: 50.",
    )

    args = parser.parse_args()

    create_template(
        input_path=args.input,
        output_path=args.output,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()