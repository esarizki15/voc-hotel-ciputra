import json
from typing import Any, Dict, List, Tuple

import pandas as pd


class ReviewAggregator:
    """
    Agregasi hasil analisis review untuk dashboard
    Voice of Customer.

    Dataset saat ini:
        IndoNLU TERMA

    Data Ciputra aktual:
        Belum digunakan.

    Struktur data dirancang agar nantinya dapat digunakan
    untuk multi-hotel.
    """

    REQUIRED_ASPECT_COLUMNS = [
        "review_id",
        "hotel_name",
        "category",
        "target",
        "opinion",
        "sentiment",
        "review_text",
    ]

    REQUIRED_REVIEW_COLUMNS = [
        "review_id",
        "hotel_name",
        "review_text",
        "date",
    ]

    def __init__(
        self,
        json_filepath: str = "data/processed_reviews.json",
    ):
        self.json_filepath = json_filepath

        self.raw_data = self._load_data()

        (
            self.df_aspects,
            self.df_reviews,
        ) = self._process_dataframe()

    # ========================================================
    # LOAD DATA
    # ========================================================

    def _load_data(self) -> List[Dict[str, Any]]:

        try:

            with open(
                self.json_filepath,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            return (
                data
                if isinstance(data, list)
                else []
            )

        except FileNotFoundError:

            print(
                f"[Aggregator] File tidak ditemukan: "
                f"{self.json_filepath}"
            )

            return []

        except (
            json.JSONDecodeError,
            OSError,
        ) as exc:

            print(
                f"[Aggregator] Gagal membaca data: "
                f"{exc}"
            )

            return []

    # ========================================================
    # SENTIMENT
    # ========================================================

    @staticmethod
    def _safe_sentiment(value: Any) -> str:

        sentiment = str(
            value or "netral"
        ).strip().lower()

        if sentiment not in {
            "positif",
            "negatif",
            "netral",
        }:
            return "netral"

        return sentiment

    # ========================================================
    # DATAFRAME
    # ========================================================

    def _process_dataframe(
        self,
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:

        aspect_records = []
        review_records = []

        if not self.raw_data:

            return (
                pd.DataFrame(
                    columns=self.REQUIRED_ASPECT_COLUMNS
                ),
                pd.DataFrame(
                    columns=self.REQUIRED_REVIEW_COLUMNS
                ),
            )

        for index, item in enumerate(
            self.raw_data
        ):

            if not isinstance(item, dict):
                continue

            review_id = str(
                item.get(
                    "review_id",
                    f"REV-{index + 1:05d}",
                )
            )

            hotel_name = str(
                item.get(
                    "hotel_name",
                    "Dataset TERMA",
                )
                or "Dataset TERMA"
            )

            review_text = str(
                item.get(
                    "review_text",
                    "",
                )
            ).strip()

            date = item.get("date")

            # ------------------------------------------------
            # REVIEW RECORD
            # ------------------------------------------------

            review_records.append(
                {
                    "review_id": review_id,
                    "hotel_name": hotel_name,
                    "review_text": review_text,
                    "date": date,
                }
            )

            # ------------------------------------------------
            # ASPECT RECORD
            # ------------------------------------------------

            aspects = item.get(
                "aspects",
                [],
            )

            if not isinstance(
                aspects,
                list,
            ):
                continue

            for aspect in aspects:

                if not isinstance(
                    aspect,
                    dict,
                ):
                    continue

                category = str(
                    aspect.get(
                        "category",
                        "Lainnya",
                    )
                    or "Lainnya"
                ).strip()

                target = str(
                    aspect.get(
                        "target",
                        "-",
                    )
                    or "-"
                ).strip()

                opinion = str(
                    aspect.get(
                        "opinion",
                        "-",
                    )
                    or "-"
                ).strip()

                sentiment = self._safe_sentiment(
                    aspect.get("sentiment")
                )

                aspect_records.append(
                    {
                        "review_id": review_id,
                        "hotel_name": hotel_name,
                        "category": category,
                        "target": target,
                        "opinion": opinion,
                        "sentiment": sentiment,
                        "review_text": review_text,
                    }
                )

        return (
            pd.DataFrame(
                aspect_records,
                columns=self.REQUIRED_ASPECT_COLUMNS,
            ),
            pd.DataFrame(
                review_records,
                columns=self.REQUIRED_REVIEW_COLUMNS,
            ),
        )

    # ========================================================
    # HOTEL
    # ========================================================

    def get_available_hotels(
        self,
    ) -> List[str]:

        if self.df_reviews.empty:
            return []

        return sorted(
            self.df_reviews[
                "hotel_name"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

    def filter_by_hotel(
        self,
        hotel_name: str,
    ) -> "ReviewAggregator":

        if (
            not hotel_name
            or hotel_name == "Semua Hotel"
        ):
            return self

        filtered = [
            item
            for item in self.raw_data
            if str(
                item.get(
                    "hotel_name",
                    "Dataset TERMA",
                )
            )
            == hotel_name
        ]

        instance = object.__new__(
            ReviewAggregator
        )

        instance.json_filepath = (
            self.json_filepath
        )

        instance.raw_data = filtered

        (
            instance.df_aspects,
            instance.df_reviews,
        ) = instance._process_dataframe()

        return instance

    # ========================================================
    # ASPECT SUMMARY
    # ========================================================

    def get_aspect_summary(
        self,
    ) -> pd.DataFrame:

        if self.df_aspects.empty:
            return pd.DataFrame()

        grouped = self.df_aspects.groupby(
            "category",
            dropna=False,
        )

        summary = []

        for category, group in grouped:

            total_mentions = len(group)

            positive_count = int(
                (
                    group["sentiment"]
                    == "positif"
                ).sum()
            )

            negative_count = int(
                (
                    group["sentiment"]
                    == "negatif"
                ).sum()
            )

            neutral_count = int(
                (
                    group["sentiment"]
                    == "netral"
                ).sum()
            )

            negative_ratio = (
                negative_count
                / total_mentions
                if total_mentions
                else 0.0
            )

            positive_ratio = (
                positive_count
                / total_mentions
                if total_mentions
                else 0.0
            )

            priority_score = round(
                total_mentions
                * negative_ratio
                * 10,
                1,
            )

            summary.append(
                {
                    "category": str(category),
                    "total_mentions": total_mentions,
                    "positive_count": positive_count,
                    "negative_count": negative_count,
                    "neutral_count": neutral_count,
                    "negative_ratio": round(
                        negative_ratio * 100,
                        1,
                    ),
                    "positive_ratio": round(
                        positive_ratio * 100,
                        1,
                    ),
                    "priority_score": priority_score,
                }
            )

        if not summary:
            return pd.DataFrame()

        return (
            pd.DataFrame(summary)
            .sort_values(
                by=[
                    "priority_score",
                    "negative_count",
                    "total_mentions",
                ],
                ascending=[
                    False,
                    False,
                    False,
                ],
            )
            .reset_index(drop=True)
        )

    # ========================================================
    # PRIORITY
    # ========================================================

    def get_top_priorities(
        self,
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:

        df_summary = (
            self.get_aspect_summary()
        )

        if df_summary.empty:
            return []

        result = df_summary[
            df_summary["negative_count"] > 0
        ].head(top_n)

        return result.to_dict(
            "records"
        )

    # ========================================================
    # STRENGTH
    # ========================================================

    def get_top_strengths(
        self,
        top_n: int = 5,
    ) -> List[Dict[str, Any]]:

        df_summary = (
            self.get_aspect_summary()
        )

        if df_summary.empty:
            return []

        eligible = df_summary[
            df_summary["total_mentions"] >= 2
        ].copy()

        if eligible.empty:
            eligible = df_summary.copy()

        result = eligible[
            eligible["positive_count"] > 0
        ].sort_values(
            by=[
                "positive_ratio",
                "positive_count",
                "total_mentions",
            ],
            ascending=[
                False,
                False,
                False,
            ],
        ).head(top_n)

        return result.to_dict(
            "records"
        )

    # ========================================================
    # KPI
    # ========================================================

    def calculate_kpis(
        self,
    ) -> Dict[str, Any]:

        total_reviews = len(
            self.df_reviews
        )

        if total_reviews == 0:

            return {
                "total_reviews": 0,
                "positive_aspect_percentage": 0.0,
                "top_priority": "Belum ada data",
                "top_strength": "Belum ada data",
            }

        if self.df_aspects.empty:

            return {
                "total_reviews": total_reviews,
                "positive_aspect_percentage": 0.0,
                "top_priority": "Belum ada data",
                "top_strength": "Belum ada data",
            }

        total_aspects = len(
            self.df_aspects
        )

        positive_aspects = int(
            (
                self.df_aspects[
                    "sentiment"
                ]
                == "positif"
            ).sum()
        )

        positive_percentage = round(
            positive_aspects
            / total_aspects
            * 100,
            1,
        )

        priorities = (
            self.get_top_priorities(1)
        )

        strengths = (
            self.get_top_strengths(1)
        )

        return {
            "total_reviews": total_reviews,
            "positive_aspect_percentage": positive_percentage,
            "top_priority": (
                priorities[0]["category"]
                if priorities
                else "Tidak ada"
            ),
            "top_strength": (
                strengths[0]["category"]
                if strengths
                else "Tidak ada"
            ),
        }

    # ========================================================
    # EVIDENCE
    # ========================================================

    def get_evidence(
        self,
        category_name: str,
        max_samples: int = 3,
    ) -> Dict[str, Any]:

        if (
            self.df_aspects.empty
            or not category_name
        ):
            return {}

        df_category = (
            self.df_aspects[
                self.df_aspects["category"]
                == category_name
            ]
        )

        if df_category.empty:
            return {}

        total_mentions = len(
            df_category
        )

        negative_count = int(
            (
                df_category["sentiment"]
                == "negatif"
            ).sum()
        )

        positive_count = int(
            (
                df_category["sentiment"]
                == "positif"
            ).sum()
        )

        negative_ratio = round(
            negative_count
            / total_mentions
            * 100,
            1,
        )

        negative_reviews = (
            df_category[
                df_category["sentiment"]
                == "negatif"
            ]["review_text"]
            .dropna()
            .drop_duplicates()
            .tolist()
        )

        examples = negative_reviews[
            :max_samples
        ]

        if len(examples) < max_samples:

            all_reviews = (
                df_category["review_text"]
                .dropna()
                .drop_duplicates()
                .tolist()
            )

            for review in all_reviews:

                if review not in examples:
                    examples.append(review)

                if (
                    len(examples)
                    >= max_samples
                ):
                    break

        return {
            "category": category_name,
            "total_mentions": total_mentions,
            "negative_count": negative_count,
            "positive_count": positive_count,
            "negative_ratio": negative_ratio,
            "example_reviews": examples,
        }

    # ========================================================
    # EXECUTIVE SUMMARY
    # ========================================================

    def generate_executive_summary_text(
        self,
    ) -> str:

        kpis = self.calculate_kpis()

        priorities = (
            self.get_top_priorities(1)
        )

        strengths = (
            self.get_top_strengths(1)
        )

        if kpis["total_reviews"] == 0:

            return (
                "Belum cukup data untuk "
                "menghasilkan ringkasan "
                "insight eksekutif."
            )

        if (
            not priorities
            and not strengths
        ):

            return (
                f"Berdasarkan "
                f"{kpis['total_reviews']:,} ulasan, "
                "belum terdapat cukup hasil "
                "analisis aspek untuk menghasilkan "
                "prioritas atau keunggulan layanan."
            )

        parts = [
            f"Berdasarkan analisis terhadap "
            f"{kpis['total_reviews']:,} ulasan."
        ]

        if priorities:

            priority = priorities[0]

            parts.append(
                f"Aspek {priority['category']} "
                "menjadi prioritas perbaikan "
                "utama dengan "
                f"{priority['negative_count']} "
                "keluhan dari "
                f"{priority['total_mentions']} "
                "penyebutan "
                f"({priority['negative_ratio']}% negatif)."
            )

        if strengths:

            strength = strengths[0]

            parts.append(
                f"Di sisi lain, "
                f"{strength['category']} "
                "menjadi salah satu keunggulan "
                "layanan dengan "
                f"{strength['positive_ratio']}% "
                "sentimen positif."
            )

        parts.append(
            "Temuan ini dapat digunakan "
            "sebagai dasar untuk menentukan "
            "area yang perlu dievaluasi lebih lanjut."
        )

        return " ".join(parts)

    def get_aspect_details(
        self,
        category_name: str,
        sentiment: str | None = None,
    ) -> List[Dict[str, Any]]:
        """
        Mengambil detail setiap penyebutan aspek berdasarkan
        kategori dan optional sentiment.

        Contoh hasil:

        {
            "review_id": "1",
            "review_text": "...",
            "category": "AC",
            "target": "AC kamar",
            "opinion": "tidak berfungsi optimal",
            "sentiment": "negatif"
        }
        """

        if self.df_aspects.empty or not category_name:
            return []

        df = self.df_aspects[
            self.df_aspects["category"].astype(str).str.strip().str.lower()
            == str(category_name).strip().lower()
        ].copy()

        if df.empty:
            return []

        if sentiment:
            normalized_sentiment = (
                str(sentiment)
                .strip()
                .lower()
            )

            df = df[
                df["sentiment"].astype(str).str.strip().str.lower()
                == normalized_sentiment
            ]

        if df.empty:
            return []

        details = []

        for _, row in df.iterrows():

            details.append(
                {
                    "review_id": str(
                        row.get(
                            "review_id",
                            "-",
                        )
                    ),
                    "review_text": str(
                        row.get(
                            "review_text",
                            "",
                        )
                    ),
                    "category": str(
                        row.get(
                            "category",
                            category_name,
                        )
                    ),
                    "target": str(
                        row.get(
                            "target",
                            "-",
                        )
                    ),
                    "opinion": str(
                        row.get(
                            "opinion",
                            "-",
                        )
                    ),
                    "sentiment": str(
                        row.get(
                            "sentiment",
                            "netral",
                        )
                    ),
                }
            )

        return details