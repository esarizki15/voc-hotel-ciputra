import json
import re
from typing import Any, Dict, List

import requests


class OllamaABSAClient:
    """
    Client Ollama untuk analisis Aspect-Based Sentiment Analysis (ABSA)
    pada ulasan hotel berbahasa Indonesia.
    """

    ALLOWED_SENTIMENTS = {"positif", "negatif", "netral"}

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "qwen3:8b",
        timeout: int = 120,
    ):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name
        self.timeout = timeout

    def _build_prompt(self, review_text: str) -> str:
        return f"""
Anda adalah AI untuk analisis Voice of Customer pada industri perhotelan.

Tugas Anda adalah melakukan Aspect-Based Sentiment Analysis (ABSA)
terhadap ulasan pelanggan hotel berbahasa Indonesia.

ULASAN:
"{review_text}"

TUGAS:
1. Identifikasi semua aspek layanan atau fasilitas yang benar-benar disebutkan.
2. Normalisasi aspek ke kategori umum jika sesuai.
3. Jika tidak ada kategori umum yang sesuai, buat kategori yang relevan.
4. Jangan memaksakan kategori jika aspek tidak disebutkan.
5. Ekstrak target spesifik yang disebut pelanggan.
6. Ekstrak opinion berupa kata atau frasa yang menunjukkan penilaian pelanggan.
7. Tentukan sentimen:
   - "positif"
   - "negatif"
   - "netral"
8. Jangan membuat aspek yang tidak disebutkan.
9. Jangan membuat fakta, opini, atau pengalaman yang tidak terdapat pada ulasan.
10. Jika satu ulasan memiliki beberapa aspek, ekstrak semuanya.

KATEGORI UMUM:
- WiFi
- Pelayanan Staf
- Kebersihan Kamar
- AC
- Sarapan
- Fasilitas Kamar
- Proses Check-in
- Kolam Renang
- Lokasi
- Harga
- Restoran
- Parkir
- Keamanan
- Kamar
- Kamar Mandi
- Tempat Tidur
- Kebersihan Hotel
- Fasilitas Hotel
- Lainnya

OUTPUT WAJIB JSON VALID.

Format:

{{
  "aspects": [
    {{
      "category": "WiFi",
      "target": "koneksi WiFi di lantai 5",
      "opinion": "sangat lambat",
      "sentiment": "negatif"
    }}
  ]
}}

Jika tidak ada aspek:

{{
  "aspects": []
}}

JANGAN memberikan markdown.
JANGAN memberikan penjelasan.
JANGAN memberikan teks di luar JSON.
""".strip()

    def analyze_review(self, review_text: str) -> List[Dict[str, Any]]:
        """
        Menganalisis satu review.

        Return:
            [
                {
                    "category": "...",
                    "target": "...",
                    "opinion": "...",
                    "sentiment": "positif|negatif|netral"
                }
            ]
        """

        if not review_text or not review_text.strip():
            return []

        payload = {
            "model": self.model_name,
            "prompt": self._build_prompt(review_text.strip()),
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            result = response.json()
            raw_response = result.get("response", "")

            return self._parse_json_output(raw_response)

        except requests.exceptions.RequestException as exc:
            print(f"[Ollama] Gagal terhubung: {exc}")
            return []

        except (ValueError, TypeError) as exc:
            print(f"[Ollama] Response tidak valid: {exc}")
            return []

        except Exception as exc:
            print(f"[Ollama] Error tidak terduga: {exc}")
            return []

    def _parse_json_output(
        self,
        raw_text: str,
    ) -> List[Dict[str, Any]]:
        """
        Parse output JSON dari Qwen.

        Mendukung:
        {
            "aspects": [...]
        }

        maupun:
        [...]
        """

        if not raw_text:
            return []

        try:
            data = json.loads(raw_text)

        except json.JSONDecodeError:
            # Fallback jika model memberikan sedikit teks
            # sebelum/sesudah JSON.
            match = re.search(
                r"\{.*\}|\[.*\]",
                raw_text,
                re.DOTALL,
            )

            if not match:
                return []

            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                return []

        if isinstance(data, dict):
            items = data.get("aspects", [])

        elif isinstance(data, list):
            items = data

        else:
            return []

        if not isinstance(items, list):
            return []

        valid_items: List[Dict[str, Any]] = []

        for item in items:
            if not isinstance(item, dict):
                continue

            category = str(
                item.get("category", "")
            ).strip()

            target = str(
                item.get("target", "")
            ).strip()

            opinion = str(
                item.get("opinion", "")
            ).strip()

            sentiment = str(
                item.get("sentiment", "netral")
            ).lower().strip()

            if not category:
                continue

            if sentiment not in self.ALLOWED_SENTIMENTS:
                sentiment = "netral"

            valid_items.append(
                {
                    "category": category,
                    "target": target or "-",
                    "opinion": opinion or "-",
                    "sentiment": sentiment,
                }
            )

        return valid_items

    def is_available(self) -> bool:
        """
        Mengecek apakah Ollama dapat diakses.
        """

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            return response.ok

        except requests.RequestException:
            return False

    def model_exists(self) -> bool:
        """
        Mengecek apakah model yang dikonfigurasi tersedia di Ollama.
        """

        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5,
            )

            response.raise_for_status()

            data = response.json()

            models = data.get("models", [])

            for model in models:
                name = model.get("name", "")

                if name == self.model_name:
                    return True

            return False

        except Exception:
            return False