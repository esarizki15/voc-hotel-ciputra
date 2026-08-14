import json
import re
from typing import Any, Dict, List, Optional

import requests


class OllamaABSAClient:
    """
    Client untuk melakukan Aspect-Based Sentiment Analysis
    menggunakan Ollama + Qwen3:8B.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "qwen3:8b",
        timeout: int = 300,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    # ========================================================
    # OLLAMA STATUS
    # ========================================================

    def is_available(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            return response.status_code == 200

        except requests.RequestException:
            return False

    # ========================================================
    # MODEL CHECK
    # ========================================================

    def is_model_available(self) -> bool:
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            if response.status_code != 200:
                return False

            data = response.json()

            models = data.get("models", [])

            for item in models:

                name = str(
                    item.get("name", "")
                ).strip().lower()

                if name == self.model.lower():
                    return True

            return False

        except Exception:
            return False

    # ========================================================
    # PROMPT
    # ========================================================

    def _build_prompt(
        self,
        review: str,
    ) -> str:

        return f"""
Anda adalah AI untuk Voice of Customer Intelligence
pada industri perhotelan.

Tugas Anda adalah melakukan Aspect-Based Sentiment Analysis
(ABSA) terhadap ulasan pelanggan berikut.

ULASAN:
"{review}"

Identifikasi semua aspek layanan atau fasilitas yang
dibicarakan pelanggan.

Untuk setiap aspek berikan:

1. category
   Kategori umum dari aspek.
   Contoh:
   - Kamar
   - AC
   - WiFi
   - Staff
   - Kebersihan
   - Lokasi
   - Makanan
   - Fasilitas

2. target
   Objek spesifik yang dibicarakan.

3. opinion
   Kata/frasa yang menunjukkan penilaian pelanggan.

4. sentiment
   Harus salah satu:
   - positif
   - negatif
   - netral

ATURAN:

- Jangan membuat aspek yang tidak disebutkan.
- Jangan menambahkan informasi yang tidak ada.
- Satu aspek dapat memiliki satu sentiment.
- Jika satu review membahas beberapa aspek,
  kembalikan semuanya.
- Gunakan Bahasa Indonesia.
- Output HARUS berupa JSON valid.
- Jangan memberikan penjelasan tambahan.
- Jangan menggunakan markdown code block.

Format output:

[
  {{
    "category": "AC",
    "target": "AC kamar",
    "opinion": "tidak dingin",
    "sentiment": "negatif"
  }}
]

Jika tidak ada aspek yang relevan:

[]

ULASAN:
"{review}"
"""

    # ========================================================
    # JSON EXTRACTION
    # ========================================================

    def _extract_json(
        self,
        text: str,
    ) -> Optional[List[Dict[str, Any]]]:

        if not text:
            return None

        text = text.strip()

        # ----------------------------------------------------
        # Direct JSON
        # ----------------------------------------------------

        try:

            data = json.loads(text)

            if isinstance(data, list):
                return data

            if isinstance(data, dict):

                if isinstance(
                    data.get("aspects"),
                    list,
                ):
                    return data["aspects"]

        except json.JSONDecodeError:
            pass

        # ----------------------------------------------------
        # Remove markdown fences
        # ----------------------------------------------------

        cleaned = re.sub(
            r"```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE,
        )

        cleaned = cleaned.replace(
            "```",
            "",
        ).strip()

        try:

            data = json.loads(cleaned)

            if isinstance(data, list):
                return data

            if isinstance(data, dict):

                aspects = data.get(
                    "aspects"
                )

                if isinstance(
                    aspects,
                    list,
                ):
                    return aspects

        except json.JSONDecodeError:
            pass

        # ----------------------------------------------------
        # Find JSON array
        # ----------------------------------------------------

        match = re.search(
            r"\[[\s\S]*\]",
            cleaned,
        )

        if match:

            try:

                data = json.loads(
                    match.group(0)
                )

                if isinstance(
                    data,
                    list,
                ):
                    return data

            except json.JSONDecodeError:
                pass

        return None

    # ========================================================
    # NORMALIZE
    # ========================================================

    def _normalize_results(
        self,
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:

        normalized = []

        for item in results:

            if not isinstance(
                item,
                dict,
            ):
                continue

            category = str(
                item.get(
                    "category",
                    "",
                )
            ).strip()

            target = str(
                item.get(
                    "target",
                    "",
                )
            ).strip()

            opinion = str(
                item.get(
                    "opinion",
                    "",
                )
            ).strip()

            sentiment = str(
                item.get(
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

            if not category:
                continue

            normalized.append(
                {
                    "category": category,
                    "target": target,
                    "opinion": opinion,
                    "sentiment": sentiment,
                }
            )

        return normalized

    # ========================================================
    # ANALYZE REVIEW
    # ========================================================

    def analyze_review(
        self,
        review: str,
    ) -> List[Dict[str, str]]:

        review = str(
            review or ""
        ).strip()

        if not review:
            return []

        prompt = self._build_prompt(
            review
        )

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0,
            },
        }

        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )

        response.raise_for_status()

        data = response.json()

        raw_response = str(
            data.get(
                "response",
                "",
            )
        )

        results = self._extract_json(
            raw_response
        )

        if not results:
            return []

        return self._normalize_results(
            results
        )