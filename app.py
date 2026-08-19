import glob
from pathlib import Path
import streamlit as st

from config.settings import (
    PAGE_TITLE,
    PAGE_ICON,
    PROCESSED_DATA_PATH,
    TOP_ASPECTS,
)

from engine.aggregator import ReviewAggregator
from engine.ollama_client import OllamaABSAClient

from components.header import render_header
from components.dashboard import render_dashboard
from components.live_analyzer import render_live_analyzer
from components.upload import render_upload


# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOAD ENGINE WITH CACHING
# ============================================================
@st.cache_resource
def load_aggregator(data_path: str):
    return ReviewAggregator(data_path)


@st.cache_resource
def load_ollama_client():
    return OllamaABSAClient()


ollama_client = load_ollama_client()


@st.cache_data(ttl=600)
def get_filtered_aggregator(hotel_name: str, data_path: str):
    agg = load_aggregator(data_path)
    return agg.filter_by_hotel(hotel_name)


# ============================================================
# HEADER
# ============================================================
render_header()


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🏨 Voice of Customer")
    st.caption("AI-Powered Voice of Customer Intelligence untuk industri perhotelan.")
    st.divider()

    st.markdown("### 📂 Sumber Data")

    # Scan seluruh file JSON hasil analisis di folder data/
    json_files = sorted(glob.glob("data/*.json"))

    if json_files:
        dataset_options = {}
        for filepath in json_files:
            # Format label tampilan agar rapi
            label = (
                Path(filepath)
                .stem.replace("processed_", "")
                .replace("_", " ")
                .replace("-", " ")
                .title()
            )
            dataset_options[label] = filepath

        # Ambil dataset aktif dari session_state atau file default
        active_path = st.session_state.get("active_dataset", str(PROCESSED_DATA_PATH))
        
        default_idx = 0
        if active_path in dataset_options.values():
            default_idx = list(dataset_options.values()).index(active_path)

        selected_label = st.selectbox(
            "Pilih Dataset Hasil Analisis:",
            options=list(dataset_options.keys()),
            index=default_idx,
        )

        selected_data_path = dataset_options[selected_label]
        st.session_state["active_dataset"] = selected_data_path
    else:
        selected_data_path = str(PROCESSED_DATA_PATH)
        st.caption("Belum ada dataset JSON ditemukan di `data/`.")

    # Load Aggregator sesuai dataset yang dipilih
    base_aggregator = load_aggregator(selected_data_path)
    available_hotels = base_aggregator.get_available_hotels()

    if available_hotels:
        hotel_options = ["Semua Hotel"] + available_hotels
        selected_hotel = st.selectbox("Pilih Hotel / Sumber", hotel_options)
        active_aggregator = get_filtered_aggregator(selected_hotel, selected_data_path)
    else:
        active_aggregator = base_aggregator
        st.caption("Dataset belum memiliki metadata hotel spesifik.")

    st.divider()

    st.markdown("### 🤖 Teknologi")
    st.write("**Model:** Qwen3:8B")
    st.write("**Inference:** Ollama Local")
    st.write("**Metode:** Aspect-Based Sentiment Analysis")

    st.divider()
    st.caption("Proof of Concept — Ciputra Group")


# ============================================================
# TABS
# ============================================================
tab_dashboard, tab_live, tab_upload = st.tabs(
    [
        "📊 Dashboard Inteligensi Pelanggan",
        "🔍 Analisis Ulasan Langsung",
        "📂 Upload & Analisis Dataset",
    ]
)


# ============================================================
# DASHBOARD
# ============================================================
with tab_dashboard:
    render_dashboard(
        active_aggregator,
        TOP_ASPECTS,
    )


# ============================================================
# LIVE ANALYZER
# ============================================================
with tab_live:
    render_live_analyzer(ollama_client)


# ============================================================
# UPLOAD
# ============================================================
with tab_upload:
    render_upload()


# ============================================================
# FOOTER
# ============================================================
st.divider()
st.caption(
    "AI-Powered Voice of Customer Intelligence · "
    "Proof of Concept · Ciputra Group"
)