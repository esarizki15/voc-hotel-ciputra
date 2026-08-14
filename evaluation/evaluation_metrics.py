"""
Evaluation metrics untuk PoC AI-Powered Voice of Customer Intelligence.

PENTING:
File ini digunakan ketika kita sudah memiliki ground truth / gold label.
Dataset TERMA yang sedang dipakai untuk PoC tidak otomatis menjadi ground
truth untuk output Qwen3:8B. Jika ingin mengevaluasi model, kita perlu
menyediakan data berlabel yang formatnya sesuai.

Format ground truth yang didukung:

[
  {
    "review_id": 1,
    "review_text": "kamar bersih tetapi wifi lambat",
    "gold_aspects": [
      {
        "category": "Kebersihan Kamar",
        "sentiment": "positif"
      },
      {
        "category": "WiFi",
        "sentiment": "negatif"
      }
    ]
  }
]

Format prediction:

[
  {
    "review_id": 1,
    "review_text": "kamar bersih tetapi wifi lambat",
    "aspects": [
      {
        "category": "Kebersihan Kamar",
        "sentiment": "positif"
      },
      {
        "category": "WiFi",
        "sentiment": "negatif"
      }
    ]
  }
]

Metrics:
- Aspect category Precision / Recall / F1
- Sentiment Accuracy
- Sentiment Macro F1
- Aspect-Sentiment pair Precision / Recall / F1
- Exact Match Rate per review

Catatan:
Evaluasi kategori menggunakan exact match setelah normalisasi sederhana.
Variasi penulisan kategori yang sebenarnya sama perlu dinormalisasi lebih
lanjut jika dataset gold sudah tersedia.
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)


VALID_SENTIMENTS = {"positif", "negatif", "netral"}


def normalize_text(value: Any) -> str:
    """Normalisasi teks sederhana agar perbandingan lebih konsisten."""
    text = str(value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_category(value: Any) -> str:
    """Normalisasi nama kategori untuk evaluasi exact match."""
    text = normalize_text(value)
    text = text.replace("_", " ")
    text = text.replace("-", " ")
    return text


def normalize_sentiment(value: Any) -> str:
    sentiment = normalize_text(value)
    return sentiment if sentiment in VALID_SENTIMENTS else "netral"


def load_json(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"Format JSON harus berupa list: {path}")

    return data


def extract_aspect_pairs(
    item: Dict[str, Any],
    aspect_key: str,
) -> List[Tuple[str, str]]:
    aspects = item.get(aspect_key, [])

    if not isinstance(aspects, list):
        return []

    pairs = []

    for aspect in aspects:
        if not isinstance(aspect, dict):
            continue

        category = normalize_category(aspect.get("category"))
        sentiment = normalize_sentiment(aspect.get("sentiment"))

        if not category:
            continue

        pairs.append((category, sentiment))

    return pairs


def match_by_review_id(
    gold_data: List[Dict[str, Any]],
    prediction_data: List[Dict[str, Any]],
) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
    """
    Memasangkan gold dan prediction berdasarkan review_id.

    Jika review_id tidak tersedia, fallback ke urutan data.
    """
    prediction_map = {
        str(item.get("review_id")): item
        for item in prediction_data
        if isinstance(item, dict) and item.get("review_id") is not None
    }

    matched = []

    for index, gold in enumerate(gold_data):
        if not isinstance(gold, dict):
            continue

        review_id = gold.get("review_id")

        if review_id is not None and str(review_id) in prediction_map:
            matched.append((gold, prediction_map[str(review_id)]))
        elif index < len(prediction_data):
            prediction = prediction_data[index]
            if isinstance(prediction, dict):
                matched.append((gold, prediction))

    return matched


def calculate_set_metrics(
    gold_sets: List[set],
    prediction_sets: List[set],
) -> Dict[str, float]:
    """
    Menghitung micro precision/recall/F1 untuk himpunan aspek.

    TP = aspek yang benar-benar ada di gold dan diprediksi model.
    FP = aspek yang diprediksi tetapi tidak ada di gold.
    FN = aspek yang ada di gold tetapi tidak diprediksi.
    """
    true_positive = 0
    false_positive = 0
    false_negative = 0

    for gold, prediction in zip(gold_sets, prediction_sets):
        true_positive += len(gold & prediction)
        false_positive += len(prediction - gold)
        false_negative += len(gold - prediction)

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def evaluate(
    gold_data: List[Dict[str, Any]],
    prediction_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    matched_reviews = match_by_review_id(gold_data, prediction_data)

    if not matched_reviews:
        raise ValueError(
            "Tidak ada review yang berhasil dipasangkan antara gold dan prediction."
        )

    gold_category_sets = []
    prediction_category_sets = []

    gold_pair_sets = []
    prediction_pair_sets = []

    gold_sentiments = []
    prediction_sentiments = []

    exact_match_count = 0

    for gold, prediction in matched_reviews:
        gold_pairs = extract_aspect_pairs(gold, "gold_aspects")
        prediction_pairs = extract_aspect_pairs(prediction, "aspects")

        gold_categories = {category for category, _ in gold_pairs}
        prediction_categories = {category for category, _ in prediction_pairs}

        gold_category_sets.append(gold_categories)
        prediction_category_sets.append(prediction_categories)

        gold_pair_sets.append(set(gold_pairs))
        prediction_pair_sets.append(set(prediction_pairs))

        if gold_categories == prediction_categories:
            exact_match_count += 1

        # Sentiment dievaluasi pada aspect category yang sama-sama ditemukan.
        gold_map = dict(gold_pairs)
        prediction_map = dict(prediction_pairs)

        common_categories = sorted(
            set(gold_map.keys()) & set(prediction_map.keys())
        )

        for category in common_categories:
            gold_sentiments.append(gold_map[category])
            prediction_sentiments.append(prediction_map[category])

    aspect_metrics = calculate_set_metrics(
        gold_category_sets,
        prediction_category_sets,
    )

    pair_metrics = calculate_set_metrics(
        gold_pair_sets,
        prediction_pair_sets,
    )

    if gold_sentiments:
        sentiment_accuracy = accuracy_score(
            gold_sentiments,
            prediction_sentiments,
        )

        sentiment_macro_f1 = f1_score(
            gold_sentiments,
            prediction_sentiments,
            labels=["positif", "negatif", "netral"],
            average="macro",
            zero_division=0,
        )

        sentiment_weighted_f1 = f1_score(
            gold_sentiments,
            prediction_sentiments,
            labels=["positif", "negatif", "netral"],
            average="weighted",
            zero_division=0,
        )

        sentiment_precision = precision_score(
            gold_sentiments,
            prediction_sentiments,
            labels=["positif", "negatif", "netral"],
            average="macro",
            zero_division=0,
        )

        sentiment_recall = recall_score(
            gold_sentiments,
            prediction_sentiments,
            labels=["positif", "negatif", "netral"],
            average="macro",
            zero_division=0,
        )
    else:
        sentiment_accuracy = 0.0
        sentiment_macro_f1 = 0.0
        sentiment_weighted_f1 = 0.0
        sentiment_precision = 0.0
        sentiment_recall = 0.0

    total_reviews = len(matched_reviews)

    return {
        "reviews_evaluated": total_reviews,
        "aspect_category": aspect_metrics,
        "aspect_sentiment_pair": pair_metrics,
        "sentiment": {
            "accuracy": round(float(sentiment_accuracy), 4),
            "macro_precision": round(float(sentiment_precision), 4),
            "macro_recall": round(float(sentiment_recall), 4),
            "macro_f1": round(float(sentiment_macro_f1), 4),
            "weighted_f1": round(float(sentiment_weighted_f1), 4),
            "evaluated_aspects": len(gold_sentiments),
        },
        "exact_match_rate": round(
            exact_match_count / total_reviews,
            4,
        ),
    }


def print_report(metrics: Dict[str, Any]) -> None:
    print()
    print("=" * 60)
    print("EVALUATION REPORT — ABSA Qwen3:8B")
    print("=" * 60)

    print(f"Reviews evaluated : {metrics['reviews_evaluated']}")

    aspect = metrics["aspect_category"]
    print()
    print("ASPECT CATEGORY")
    print(f"  Precision : {aspect['precision']:.4f}")
    print(f"  Recall    : {aspect['recall']:.4f}")
    print(f"  F1        : {aspect['f1']:.4f}")

    sentiment = metrics["sentiment"]
    print()
    print("SENTIMENT")
    print(f"  Accuracy      : {sentiment['accuracy']:.4f}")
    print(f"  Macro F1      : {sentiment['macro_f1']:.4f}")
    print(f"  Weighted F1   : {sentiment['weighted_f1']:.4f}")
    print(f"  Evaluated     : {sentiment['evaluated_aspects']} aspects")

    pair = metrics["aspect_sentiment_pair"]
    print()
    print("ASPECT + SENTIMENT")
    print(f"  Precision : {pair['precision']:.4f}")
    print(f"  Recall    : {pair['recall']:.4f}")
    print(f"  F1        : {pair['f1']:.4f}")

    print()
    print(
        f"Exact Match Rate : {metrics['exact_match_rate']:.4f}"
    )

    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate hasil ABSA Qwen3:8B menggunakan ground truth."
    )

    parser.add_argument(
        "--gold",
        type=Path,
        required=True,
        help="Path JSON ground truth/gold label.",
    )

    parser.add_argument(
        "--prediction",
        type=Path,
        default=Path("data/processed_reviews.json"),
        help="Path JSON hasil prediksi model.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Opsional: simpan metrics ke file JSON.",
    )

    args = parser.parse_args()

    try:
        gold_data = load_json(args.gold)
        prediction_data = load_json(args.prediction)

        metrics = evaluate(
            gold_data=gold_data,
            prediction_data=prediction_data,
        )

        print_report(metrics)

        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)

            with args.output.open("w", encoding="utf-8") as file:
                json.dump(
                    metrics,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            print(f"Metrics disimpan ke: {args.output}")

    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"❌ Evaluation gagal: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()