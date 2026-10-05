import re
from typing import Any, Dict, List, Set, Tuple

# Kategori = entitas yang dibicarakan. Sisi kualitasnya (bersih, nyaman, mahal, dll)
# ditangkap oleh "opinion" dan "sentiment", sedangkan objek spesifiknya oleh "target".
CATEGORY_DESCRIPTIONS: Dict[str, str] = {
    "Kamar": "kamar tidur beserta isinya (tempat tidur, AC, TV, kebersihan kamar, kebisingan kamar)",
    "Kamar Mandi": "kamar mandi, toilet, shower, air panas, handuk",
    "Makanan & Minuman": "sarapan, restoran, menu, rasa makanan, room service makanan",
    "Staf & Pelayanan": "keramahan dan kecepatan staf, resepsionis, proses check-in/check-out",
    "Fasilitas Umum": "kolam renang, gym, spa, lift, lobi, area publik, kebersihan area hotel",
    "Wi-Fi": "koneksi internet",
    "Lokasi & Akses": "letak hotel, akses transportasi, pemandangan, jarak ke tempat lain",
    "Parkir": "area dan layanan parkir",
    "Harga": "harga, tarif, nilai uang",
    "Keamanan": "keamanan dan keselamatan",
    "Lainnya": "hanya jika tidak cocok dengan kategori mana pun di atas",
}

CATEGORIES: List[str] = list(CATEGORY_DESCRIPTIONS)
FALLBACK_CATEGORY = "Lainnya"

# Urutan penting: entitas yang lebih spesifik dicek lebih dulu.
# Pencocokan per kata utuh (bukan substring), jadi "nyaman" tidak cocok dengan "aman".
_KEYWORD_RULES: List[Tuple[str, Set[str]]] = [
    ("Harga", {"harga", "price", "pricing", "tarif", "biaya", "cost", "value", "mahal", "murah"}),
    ("Kamar Mandi", {"mandi", "toilet", "bathroom", "shower", "wc"}),
    ("Wi-Fi", {"wifi", "internet", "koneksi", "connection"}),
    ("Parkir", {"parkir", "parking"}),
    (
        "Makanan & Minuman",
        {
            "makan", "makanan", "minum", "minuman", "resto", "restoran", "restaurant",
            "sarapan", "breakfast", "food", "dining", "menu", "buffet", "kuliner",
        },
    ),
    (
        "Staf & Pelayanan",
        {
            "staf", "staff", "pelayanan", "layanan", "service", "resepsionis",
            "receptionist", "checkin", "checkout", "check", "pegawai", "karyawan",
            "satpam", "concierge",
        },
    ),
    ("Keamanan", {"keamanan", "aman", "security", "safety", "safe"}),
    (
        "Lokasi & Akses",
        {
            "lokasi", "location", "akses", "access", "pemandangan", "view",
            "strategis", "jarak", "letak",
        },
    ),
    (
        "Kamar",
        {
            "kamar", "room", "rooms", "ac", "pendingin", "kasur", "bed", "tidur",
            "bantal", "seprai", "tv", "televisi", "suite",
        },
    ),
    (
        "Fasilitas Umum",
        {
            "fasilitas", "facility", "facilities", "kolam", "renang", "pool", "gym",
            "spa", "lift", "elevator", "lobi", "lobby", "hotel", "kebersihan",
            "cleanliness", "bersih", "clean",
        },
    ),
]


def normalize_category(raw_category: Any) -> str:
    """Petakan kategori mentah (dari LLM atau data lama) ke salah satu CATEGORIES."""
    if not raw_category:
        return ""

    text = str(raw_category).strip().lower()
    if not text:
        return ""

    for category in CATEGORIES:
        if text == category.lower():
            return category

    text = re.sub(r"wi[\s-]*fi", "wifi", text)
    text = re.sub(r"check[\s-]*(in|out)", r"check\1", text)
    tokens = set(re.findall(r"[a-z0-9]+", text))

    for category, keywords in _KEYWORD_RULES:
        if tokens & keywords:
            return category

    return FALLBACK_CATEGORY
