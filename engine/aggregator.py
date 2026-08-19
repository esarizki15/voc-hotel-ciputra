import json
import os
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional

import pandas as pd


# ========================================================
# SMART CATEGORY CLEANING & PATTERN MATCHING
# ========================================================

def clean_category_name(raw_category: Any) -> str:
    """
    Membersihkan karakter aneh, koma/titik gantung, kata terpotong,
    dan memetakan ke nama kategori standar industri perhotelan.
    """
    if not raw_category:
        return ""

    raw_str = str(raw_category).strip().lower()

    # Hapus karakter selain huruf, angka, dan spasi (misal: "Fasilit," -> "fasilit")
    cleaned = re.sub(r"[^\w\s]", "", raw_str)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        return ""

    # --- ATURAN PATTERN MATCHING ---

    # 1. Fasilitas Hotel (menangani "fasilit,", "fasil", "fas.", "fasilitas", "facility", dll)
    if (
        cleaned.startswith("fas")
        or "facility" in cleaned
        or "facilities" in cleaned
    ):
        return "Fasilitas Hotel"

    # 2. Kebersihan Hotel
    if "bersih" in cleaned:
        return "Kebersihan Hotel"

    # 3. Pelayanan Staf
    if (
        "staf" in cleaned
        or "staff" in cleaned
        or "pelayanan" in cleaned
        or "service" in cleaned
        or "resepsionis" in cleaned
        or "receptionist" in cleaned
    ):
        return "Pelayanan Staf"

    # 4. Kamar Mandi vs Kamar
    if "mandi" in cleaned or "toilet" in cleaned or "bathroom" in cleaned:
        return "Kamar Mandi"
    elif "kamar" in cleaned or "room" in cleaned:
        return "Kamar"

    # 5. Restoran & Makanan
    if (
        "makan" in cleaned
        or "minum" in cleaned
        or "resto" in cleaned
        or "sarapan" in cleaned
        or "breakfast" in cleaned
        or "food" in cleaned
    ):
        return "Restoran"

    # 6. AC
    if cleaned in ["ac", "air conditioner", "pendingin"]:
        return "AC"

    # 7. Check-In
    if "check" in cleaned or "masuk" in cleaned:
        return "Proses Check-In"

    # 8. Parkir
    if "parkir" in cleaned or "parking" in cleaned:
        return "Parkir"

    # 9. Kolam Renang
    if "renang" in cleaned or "pool" in cleaned:
        return "Kolam Renang"

    # 10. Keamanan
    if "aman" in cleaned or "security" in cleaned:
        return "Keamanan"

    # 11. Harga
    if "harga" in cleaned or "price" in cleaned or "tarif" in cleaned:
        return "Harga"

    # 12. Pemandangan
    if "pandang" in cleaned or "view" in cleaned:
        return "Pemandangan"

    # 13. Lokasi
    if "lokasi" in cleaned or "location" in cleaned:
        return "Lokasi"

    # Jika tidak cocok dengan rule di atas, bersihkan simbol dan buat Title Case
    return str(raw_category).strip(" ,.-_").title()


class ReviewAggregator:

    def __init__(
        self,
        data_path: str,
    ):
        self.data_path = str(data_path)
        self.reviews = []
        self._load()

    # ========================================================
    # LOAD
    # ========================================================

    def _load(self):
        if not os.path.exists(self.data_path):
            self.reviews = []
            return

        try:
            with open(self.data_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                self.reviews = data
            elif isinstance(data, dict):
                self.reviews = data.get("reviews", [])
            else:
                self.reviews = []
        except Exception:
            self.reviews = []

    # ========================================================
    # SAVE
    # ========================================================

    def save(
        self,
        reviews: Optional[List[Dict[str, Any]]] = None,
    ):
        if reviews is not None:
            self.reviews = reviews

        directory = os.path.dirname(self.data_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(self.data_path, "w", encoding="utf-8") as file:
            json.dump(
                self.reviews,
                file,
                ensure_ascii=False,
                indent=2,
            )

    # ========================================================
    # RELOAD
    # ========================================================

    def reload(self):
        self._load()

    # ========================================================
    # AVAILABLE HOTELS
    # ========================================================

    def get_available_hotels(self):
        hotels = set()
        for review in self.reviews:
            hotel = review.get("hotel") or review.get("hotel_name")
            if hotel:
                hotels.add(str(hotel).strip())

        return sorted(hotels)

    # ========================================================
    # FILTER HOTEL
    # ========================================================

    def filter_by_hotel(
        self,
        hotel_name: str,
    ):
        if not hotel_name or hotel_name == "Semua Hotel":
            return self

        filtered = []
        for review in self.reviews:
            hotel = review.get("hotel") or review.get("hotel_name")
            if str(hotel).strip() == str(hotel_name).strip():
                filtered.append(review)

        instance = ReviewAggregator.__new__(ReviewAggregator)
        instance.data_path = self.data_path
        instance.reviews = filtered

        return instance

    # ========================================================
    # FLATTEN ASPECTS
    # ========================================================

    def _flatten_aspects(self):
        rows = []

        for review in self.reviews:
            review_id = review.get("review_id", "-")
            review_text = review.get("review_text", "")
            aspects = review.get("aspects", []) or review.get("aspect_sentiments", [])

            if not isinstance(aspects, list):
                continue

            for aspect in aspects:
                if not isinstance(aspect, dict):
                    continue

                raw_cat = aspect.get("category", "")
                
                # CLEANING & NORMALISASI OTOMATIS
                category = clean_category_name(raw_cat)

                if not category:
                    continue

                sentiment = (
                    str(aspect.get("sentiment", "netral"))
                    .strip()
                    .lower()
                )

                if sentiment not in ["positif", "negatif", "netral"]:
                    sentiment = "netral"

                rows.append(
                    {
                        "review_id": review_id,
                        "review_text": review_text,
                        "category": category,
                        "target": aspect.get("target", ""),
                        "opinion": aspect.get("opinion", ""),
                        "sentiment": sentiment,
                    }
                )

        return rows

    # ========================================================
    # ASPECT SUMMARY
    # ========================================================

    def get_aspect_summary(self):
        rows = self._flatten_aspects()

        if not rows:
            return pd.DataFrame(
                columns=[
                    "category",
                    "total_mentions",
                    "positif_count",
                    "negatif_count",
                    "netral_count",
                    "positive_count",
                    "negative_count",
                    "neutral_count",
                    "positive_ratio",
                    "negative_ratio",
                    "priority_score",
                ]
            )

        df = pd.DataFrame(rows)

        grouped = (
            df.groupby("category")["sentiment"]
            .value_counts()
            .unstack(fill_value=0)
        )

        for sentiment in ["positif", "negatif", "netral"]:
            if sentiment not in grouped.columns:
                grouped[sentiment] = 0

        grouped["positif_count"] = grouped["positif"]
        grouped["negatif_count"] = grouped["negatif"]
        grouped["netral_count"] = grouped["netral"]

        grouped["positive_count"] = grouped["positif"]
        grouped["negative_count"] = grouped["negatif"]
        grouped["neutral_count"] = grouped["netral"]

        grouped["total_mentions"] = (
            grouped["positif_count"]
            + grouped["negatif_count"]
            + grouped["netral_count"]
        )

        grouped["positive_ratio"] = (
            grouped["positif_count"] / grouped["total_mentions"] * 100
        ).round(1)

        grouped["negative_ratio"] = (
            grouped["negatif_count"] / grouped["total_mentions"] * 100
        ).round(1)

        grouped["priority_score"] = (
            grouped["total_mentions"]
            * (grouped["negatif_count"] / grouped["total_mentions"])
        ).round(1)

        result = grouped.reset_index().sort_values(
            "total_mentions",
            ascending=False,
        )

        return result

    # ========================================================
    # KPI
    # ========================================================

    def calculate_kpis(self):
        summary = self.get_aspect_summary()
        total_reviews = len(self.reviews)

        if summary.empty:
            return {
                "total_reviews": total_reviews,
                "positive_aspect_percentage": 0,
                "top_priority": "-",
                "top_strength": "-",
            }

        total_aspects = summary["total_mentions"].sum()
        positive_aspects = summary["positive_count"].sum()

        positive_percentage = (
            positive_aspects / total_aspects * 100 if total_aspects else 0
        )

        priority_row = summary.sort_values(
            "priority_score",
            ascending=False,
        ).iloc[0]

        strength_df = summary.copy()
        strength_df = strength_df[strength_df["total_mentions"] > 0]
        strength_df["strength_score"] = (
            strength_df["positive_count"] / strength_df["total_mentions"]
        )

        strength_df = strength_df.sort_values(
            ["strength_score", "total_mentions"],
            ascending=False,
        )

        strength = (
            strength_df.iloc[0]["category"]
            if not strength_df.empty
            else "-"
        )

        return {
            "total_reviews": total_reviews,
            "positive_aspect_percentage": positive_percentage,
            "top_priority": priority_row["category"],
            "top_strength": strength,
        }

    # ========================================================
    # TOP PRIORITIES
    # ========================================================

    def get_top_priorities(
        self,
        top_n: int = 5,
    ):
        summary = self.get_aspect_summary()

        if summary.empty:
            return []

        result = summary.sort_values(
            "priority_score",
            ascending=False,
        ).head(top_n)

        items = []
        for _, row in result.iterrows():
            if row["negative_count"] <= 0:
                continue

            items.append(
                {
                    "category": row["category"],
                    "total_mentions": int(row["total_mentions"]),
                    "negative_count": int(row["negative_count"]),
                    "negative_ratio": float(row["negative_ratio"]),
                    "priority_score": float(row["priority_score"]),
                }
            )

        return items

    # ========================================================
    # TOP STRENGTHS
    # ========================================================

    def get_top_strengths(
        self,
        top_n: int = 5,
    ):
        summary = self.get_aspect_summary()

        if summary.empty:
            return []

        summary = summary.copy()
        summary["strength_score"] = (
            summary["positive_count"] / summary["total_mentions"]
        )

        result = summary.sort_values(
            ["strength_score", "total_mentions"],
            ascending=False,
        ).head(top_n)

        items = []
        for _, row in result.iterrows():
            items.append(
                {
                    "category": row["category"],
                    "total_mentions": int(row["total_mentions"]),
                    "positive_count": int(row["positive_count"]),
                    "positive_ratio": float(row["positive_ratio"]),
                }
            )

        return items

    # ========================================================
    # EVIDENCE
    # ========================================================

    def get_evidence(
        self,
        category_name: str,
    ):
        details = self.get_aspect_details(category_name)

        if not details:
            return None

        negative_count = sum(
            1 for item in details if item["sentiment"] == "negatif"
        )

        negative_ratio = (
            negative_count / len(details) * 100 if details else 0
        )

        return {
            "total_mentions": len(details),
            "negative_count": negative_count,
            "negative_ratio": negative_ratio,
            "example_reviews": [
                item["review_text"] for item in details[:5]
            ],
        }

    # ========================================================
    # ASPECT DETAILS
    # ========================================================

    def get_aspect_details(
        self,
        category_name: str,
        sentiment: Optional[str] = None,
    ):
        rows = self._flatten_aspects()

        target_cat = clean_category_name(category_name).lower()

        if sentiment:
            sentiment = str(sentiment).strip().lower()

        result = []
        for row in rows:
            row_cat = clean_category_name(row["category"]).lower()

            if row_cat != target_cat:
                continue

            if sentiment and row["sentiment"] != sentiment:
                continue

            result.append(row)

        return result

    # ========================================================
    # EXECUTIVE SUMMARY
    # ========================================================

    def generate_executive_summary_text(self):
        summary = self.get_aspect_summary()

        if summary.empty:
            return "Belum terdapat cukup data untuk menghasilkan insight."

        priority = summary.sort_values(
            "priority_score",
            ascending=False,
        ).iloc[0]

        strength = summary.sort_values(
            "positive_ratio",
            ascending=False,
        ).iloc[0]

        return (
            f"Aspek yang paling perlu diperhatikan "
            f"adalah {priority['category']} dengan "
            f"{int(priority['negative_count'])} "
            f"sentimen negatif dari "
            f"{int(priority['total_mentions'])} "
            f"penyebutan. Sementara itu, "
            f"{strength['category']} menunjukkan "
            f"proporsi sentimen positif tertinggi "
            f"sebesar {strength['positive_ratio']:.1f}%."
        )