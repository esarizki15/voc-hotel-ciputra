import streamlit as st

from config.settings import (
    PAGE_TITLE,
    PAGE_ICON,
    PROCESSED_DATA_PATH,
    TOP_ASPECTS,
)

from engine.aggregator import (
    ReviewAggregator,
)

from engine.ollama_client import (
    OllamaABSAClient,
)

from components.header import (
    render_header,
)

from components.dashboard import (
    render_dashboard,
)

from components.live_analyzer import (
    render_live_analyzer,
)

from components.upload import (
    render_upload,
)


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
# LOAD ENGINE
# ============================================================

@st.cache_resource
def load_aggregator():

    return ReviewAggregator(
        str(PROCESSED_DATA_PATH)
    )


@st.cache_resource
def load_ollama_client():

    return OllamaABSAClient()


aggregator = load_aggregator()

ollama_client = (
    load_ollama_client()
)


# ============================================================
# HEADER
# ============================================================

render_header()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "## 🏨 Voice of Customer"
    )

    st.caption(
        "AI-Powered Voice of Customer Intelligence "
        "untuk industri perhotelan."
    )

    st.divider()

    st.markdown(
        "### 📂 Sumber Data"
    )

    st.info(
        "PoC saat ini menggunakan dataset "
        "IndoNLU TERMA."
    )

    available_hotels = (
        aggregator
        .get_available_hotels()
    )

    if available_hotels:

        hotel_options = (
            ["Semua Hotel"]
            + available_hotels
        )

        selected_hotel = st.selectbox(
            "Pilih Hotel / Sumber",
            hotel_options,
        )

        active_aggregator = (
            aggregator
            .filter_by_hotel(
                selected_hotel
            )
        )

    else:

        active_aggregator = (
            aggregator
        )

        st.caption(
            "Dataset belum memiliki "
            "metadata hotel."
        )

    st.divider()

    st.markdown(
        "### 🤖 Teknologi"
    )

    st.write(
        "**Model:** Qwen3:8B"
    )

    st.write(
        "**Inference:** Ollama Local"
    )

    st.write(
        "**Metode:** Aspect-Based "
        "Sentiment Analysis"
    )

    st.write(
        "**Dataset:** IndoNLU TERMA"
    )

    st.divider()

    st.caption(
        "Proof of Concept — Ciputra Group"
    )


# ============================================================
# TABS
# ============================================================

tab_dashboard, tab_live, tab_upload = (
    st.tabs(
        [
            "📊 Dashboard Inteligensi Pelanggan",
            "🔍 Analisis Ulasan Langsung",
            "📂 Upload & Analisis Dataset",
        ]
    )
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

    render_live_analyzer(
        ollama_client
    )


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