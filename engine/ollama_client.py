import json
import re
from typing import Any, Dict, List, Optional

import requests


class OllamaABSAClient:
    """
    Client untuk melakukan Aspect-Based Sentiment Analysis (ABSA)
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
        self.model_name = model
        self.timeout = timeout

    # ========================================================
    # OLLAMA STATUS & MODEL CHECK
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

    def model_exists(self) -> bool:
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
                name = str(item.get("name", "")).strip().lower()
                if name == self.model.lower():
                    return True

            return False
        except Exception:
            return False

    def is_model_available(self) -> bool:
        return self.model_exists()

    # ========================================================
    # PROMPT DESIGN (OPTIMIZED FOR FAST INFERENCE)
    # ========================================================

    def _build_prompt(self, review: str) -> str:
        return f"""Anda adalah AI untuk Voice of Customer Intelligence pada industri perhotelan.

Tugas Anda adalah melakukan Aspect-Based Sentiment Analysis (ABSA) terhadap ulasan pelanggan berikut.

ULASAN:
"{review}"

Identifikasi semua aspek layanan atau fasilitas yang dibicarakan pelanggan.

KATEGORI UMUM (Pilih yang paling sesuai):
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

ATURAN:
1. Setiap aspek harus memiliki:
   - "category": Salah satu dari KATEGORI UMUM di atas.
   - "target": Objek/fasilitas spesifik yang dibicarakan.
   - "opinion": Kata/frasa opini penjelas dari pelanggan.
   - "sentiment": Harus salah satu dari "positif", "negatif", atau "netral".
2. Jangan membuat aspek yang tidak disebutkan dalam ulasan.
3. Output HARUS berupa JSON valid dengan key utama "aspects".

Format output:
{{
  "aspects": [
    {{
      "category": "AC",
      "target": "AC kamar",
      "opinion": "tidak dingin",
      "sentiment": "negatif"
    }}
  ]
}}

Jika tidak ada aspek yang relevan, kembalikan:
{{
  "aspects": []
}}"""

    # ========================================================
    # JSON EXTRACTION
    # ========================================================

    def _extract_json(self, text: str) -> Optional[List[Dict[str, Any]]]:
        if not text:
            return None

        text = text.strip()

        # Direct JSON Parsing
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "aspects" in data:
                return data["aspects"]
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

        # Cleanup Markdown Code Blocks
        cleaned = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
        cleaned = cleaned.replace("```", "").strip()

        try:
            data = json.loads(cleaned)
            if isinstance(data, dict) and "aspects" in data:
                return data["aspects"]
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

        # Match JSON Object Structure
        match_obj = re.search(r"\{[\s\S]*\}", cleaned)
        if match_obj:
            try:
                data = json.loads(match_obj.group(0))
                if isinstance(data, dict) and "aspects" in data:
                    return data["aspects"]
            except json.JSONDecodeError:
                pass

        # Fallback Match JSON Array Structure
        match_arr = re.search(r"\[[\s\S]*\]", cleaned)
        if match_arr:
            try:
                data = json.loads(match_arr.group(0))
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                pass

        return None

    # ========================================================
    # DATA NORMALIZATION
    # ========================================================

    def _normalize_results(
        self, results: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        normalized = []

        if not isinstance(results, list):
            return normalized

        for item in results:
            if not isinstance(item, dict):
                continue

            category = str(item.get("category", "")).strip()
            target = str(item.get("target", "")).strip()
            opinion = str(item.get("opinion", "")).strip()
            sentiment = str(item.get("sentiment", "netral")).strip().lower()

            if sentiment not in ["positif", "negatif", "netral"]:
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
    # MAIN ANALYZE METHOD
    # ========================================================

    def analyze_review(self, review: str) -> List[Dict[str, str]]:
        review = str(review or "").strip()
        if not review:
            return []

        prompt = self._build_prompt(review)

        # Payload diatur optimal dengan format JSON native + sampling ringan
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 256,
            },
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            raw_response = str(data.get("response", ""))
            results = self._extract_json(raw_response)

            if not results:
                return []

            return self._normalize_results(results)

        except Exception as exc:
            print(f"⚠️ Error analisis ulasan: {exc}")
            return []