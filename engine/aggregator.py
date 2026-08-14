import json
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional

import pandas as pd


class ReviewAggregator:

    def __init__(
        self,
        data_path: str,
    ):
        self.data_path = data_path

        self.reviews = []

        self._load()

    # ========================================================
    # LOAD
    # ========================================================

    def _load(self):

        if not os.path.exists(
            self.data_path
        ):

            self.reviews = []

            return

        try:

            with open(
                self.data_path,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if isinstance(
                data,
                list,
            ):

                self.reviews = data

            elif isinstance(
                data,
                dict,
            ):

                self.reviews = data.get(
                    "reviews",
                    [],
                )

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

        directory = os.path.dirname(
            self.data_path
        )

        if directory:
            os.makedirs(
                directory,
                exist_ok=True,
            )

        with open(
            self.data_path,
            "w",
            encoding="utf-8",
        ) as file:

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

            hotel = (
                review.get("hotel")
                or review.get("hotel_name")
            )

            if hotel:
                hotels.add(
                    str(hotel).strip()
                )

        return sorted(
            hotels
        )

    # ========================================================
    # FILTER HOTEL
    # ========================================================

    def filter_by_hotel(
        self,
        hotel_name: str,
    ):

        if (
            not hotel_name
            or hotel_name == "Semua Hotel"
        ):
            return self

        filtered = []

        for review in self.reviews:

            hotel = (
                review.get("hotel")
                or review.get("hotel_name")
            )

            if str(
                hotel
            ).strip() == str(
                hotel_name
            ).strip():

                filtered.append(
                    review
                )

        instance = ReviewAggregator.__new__(
            ReviewAggregator
        )

        instance.data_path = self.data_path
        instance.reviews = filtered

        return instance

    # ========================================================
    # FLATTEN ASPECTS
    # ========================================================

    def _flatten_aspects(self):

        rows = []

        for review in self.reviews:

            review_id = review.get(
                "review_id",
                "-",
            )

            review_text = review.get(
                "review_text",
                "",
            )

            aspects = review.get(
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
                        "",
                    )
                ).strip()

                if not category:
                    continue

                sentiment = str(
                    aspect.get(
                        "sentiment",
                        "netral",
                    )
                ).strip().lower()

                if sentiment not in [
                    "positif",
                    "negatif",
                    "netral",
                ]:
                    sentiment = "netral"

                rows.append(
                    {
                        "review_id": review_id,
                        "review_text": review_text,
                        "category": category,
                        "target": aspect.get(
                            "target",
                            "",
                        ),
                        "opinion": aspect.get(
                            "opinion",
                            "",
                        ),
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
                    "positive_count",
                    "negative_count",
                    "neutral_count",
                    "positive_ratio",
                    "negative_ratio",
                    "priority_score",
                ]
            )

        df = pd.DataFrame(
            rows
        )

        grouped = (
            df.groupby(
                "category"
            )["sentiment"]
            .value_counts()
            .unstack(
                fill_value=0
            )
        )

        for sentiment in [
            "positif",
            "negatif",
            "netral",
        ]:

            if sentiment not in grouped.columns:

                grouped[
                    sentiment
                ] = 0

        grouped = grouped.rename(
            columns={
                "positif": "positive_count",
                "negatif": "negative_count",
                "netral": "neutral_count",
            }
        )

        grouped[
            "total_mentions"
        ] = (
            grouped[
                [
                    "positive_count",
                    "negative_count",
                    "neutral_count",
                ]
            ].sum(axis=1)
        )

        grouped[
            "positive_ratio"
        ] = (
            grouped["positive_count"]
            / grouped["total_mentions"]
            * 100
        ).round(1)

        grouped[
            "negative_ratio"
        ] = (
            grouped["negative_count"]
            / grouped["total_mentions"]
            * 100
        ).round(1)

        grouped[
            "priority_score"
        ] = (
            grouped["total_mentions"]
            * (
                grouped["negative_count"]
                / grouped["total_mentions"]
            )
        )

        grouped[
            "priority_score"
        ] = grouped[
            "priority_score"
        ].round(1)

        result = (
            grouped
            .reset_index()
            .sort_values(
                "total_mentions",
                ascending=False,
            )
        )

        return result

    # ========================================================
    # KPI
    # ========================================================

    def calculate_kpis(self):

        summary = (
            self.get_aspect_summary()
        )

        total_reviews = len(
            self.reviews
        )

        if summary.empty:

            return {
                "total_reviews": total_reviews,
                "positive_aspect_percentage": 0,
                "top_priority": "-",
                "top_strength": "-",
            }

        total_aspects = summary[
            "total_mentions"
        ].sum()

        positive_aspects = summary[
            "positive_count"
        ].sum()

        positive_percentage = (
            positive_aspects
            / total_aspects
            * 100
            if total_aspects
            else 0
        )

        priority_row = (
            summary
            .sort_values(
                "priority_score",
                ascending=False,
            )
            .iloc[0]
        )

        strength_df = summary.copy()

        strength_df = strength_df[
            strength_df[
                "total_mentions"
            ] > 0
        ]

        strength_df[
            "strength_score"
        ] = (
            strength_df[
                "positive_count"
            ]
            / strength_df[
                "total_mentions"
            ]
        )

        strength_df = (
            strength_df
            .sort_values(
                [
                    "strength_score",
                    "total_mentions",
                ],
                ascending=False,
            )
        )

        strength = (
            strength_df.iloc[0]["category"]
            if not strength_df.empty
            else "-"
        )

        return {
            "total_reviews": total_reviews,
            "positive_aspect_percentage": positive_percentage,
            "top_priority": priority_row[
                "category"
            ],
            "top_strength": strength,
        }

    # ========================================================
    # TOP PRIORITIES
    # ========================================================

    def get_top_priorities(
        self,
        top_n: int = 5,
    ):

        summary = (
            self.get_aspect_summary()
        )

        if summary.empty:
            return []

        result = (
            summary
            .sort_values(
                "priority_score",
                ascending=False,
            )
            .head(top_n)
        )

        items = []

        for _, row in result.iterrows():

            if row[
                "negative_count"
            ] <= 0:
                continue

            items.append(
                {
                    "category": row[
                        "category"
                    ],
                    "total_mentions": int(
                        row[
                            "total_mentions"
                        ]
                    ),
                    "negative_count": int(
                        row[
                            "negative_count"
                        ]
                    ),
                    "negative_ratio": float(
                        row[
                            "negative_ratio"
                        ]
                    ),
                    "priority_score": float(
                        row[
                            "priority_score"
                        ]
                    ),
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

        summary = (
            self.get_aspect_summary()
        )

        if summary.empty:
            return []

        summary = summary.copy()

        summary[
            "strength_score"
        ] = (
            summary[
                "positive_count"
            ]
            / summary[
                "total_mentions"
            ]
        )

        result = (
            summary
            .sort_values(
                [
                    "strength_score",
                    "total_mentions",
                ],
                ascending=False,
            )
            .head(top_n)
        )

        items = []

        for _, row in result.iterrows():

            items.append(
                {
                    "category": row[
                        "category"
                    ],
                    "total_mentions": int(
                        row[
                            "total_mentions"
                        ]
                    ),
                    "positive_count": int(
                        row[
                            "positive_count"
                        ]
                    ),
                    "positive_ratio": float(
                        row[
                            "positive_ratio"
                        ]
                    ),
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

        details = (
            self.get_aspect_details(
                category_name
            )
        )

        if not details:
            return None

        negative_count = sum(
            1
            for item in details
            if item["sentiment"]
            == "negatif"
        )

        negative_ratio = (
            negative_count
            / len(details)
            * 100
            if details
            else 0
        )

        return {
            "total_mentions": len(
                details
            ),
            "negative_count": negative_count,
            "negative_ratio": negative_ratio,
            "example_reviews": [
                item[
                    "review_text"
                ]
                for item in details[:5]
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

        rows = (
            self._flatten_aspects()
        )

        category_name = str(
            category_name
        ).strip().lower()

        if sentiment:

            sentiment = str(
                sentiment
            ).strip().lower()

        result = []

        for row in rows:

            if (
                str(
                    row["category"]
                )
                .strip()
                .lower()
                != category_name
            ):
                continue

            if (
                sentiment
                and row[
                    "sentiment"
                ] != sentiment
            ):
                continue

            result.append(
                row
            )

        return result

    # ========================================================
    # EXECUTIVE SUMMARY
    # ========================================================

    def generate_executive_summary_text(
        self,
    ):

        summary = (
            self.get_aspect_summary()
        )

        if summary.empty:

            return (
                "Belum terdapat cukup data "
                "untuk menghasilkan insight."
            )

        priority = (
            summary
            .sort_values(
                "priority_score",
                ascending=False,
            )
            .iloc[0]
        )

        strength = (
            summary
            .sort_values(
                "positive_ratio",
                ascending=False,
            )
            .iloc[0]
        )

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