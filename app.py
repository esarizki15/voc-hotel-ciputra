import html

import plotly.graph_objects as go
import streamlit as st

from engine.aggregator import ReviewAggregator
from engine.ollama_client import OllamaABSAClient


# ============================================================
# KONFIGURASI
# ============================================================

st.set_page_config(
    page_title="Voice of Customer Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = "data/processed_reviews.json"


# ============================================================
# CUSTOM CSS
# Gunakan CSS hanya untuk styling sederhana.
# Komponen utama menggunakan native Streamlit.
# ============================================================

st.markdown(
    """
<style>

    /* Header */
    .main-header {
        background: linear-gradient(
            135deg,
            #1e293b 0%,
            #0f172a 100%
        );
        border-bottom: 2px solid #38bdf8;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
    }

    .main-title {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 700;
        line-height: 1.3;
        margin: 0;
    }

    .main-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 8px;
        line-height: 1.5;
    }

    /* Insight */
    .insight-box {
        padding: 18px 20px;
        border-radius: 10px;
        border-left: 5px solid #2563eb;
        background-color: rgba(37, 99, 235, 0.08);
        margin: 10px 0 20px 0;
    }

    .insight-title {
        font-size: 17px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .insight-text {
        font-size: 14px;
        line-height: 1.6;
    }

    /* Priority */
    .priority-box {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 10px;
    }

    .priority-title {
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .priority-meta {
        font-size: 13px;
        opacity: 0.7;
    }

    .priority-negative {
        font-size: 14px;
        font-weight: 600;
        margin-top: 8px;
    }

    /* Evidence */
    .quote-box {
        padding: 12px 16px;
        border-left: 4px solid #ef4444;
        background-color: rgba(239, 68, 68, 0.06);
        border-radius: 0 8px 8px 0;
        margin-bottom: 10px;
        font-style: italic;
        font-size: 14px;
    }

    /* AI aspect */
    .aspect-box {
        padding: 16px;
        border-radius: 10px;
        border: 1px solid rgba(128, 128, 128, 0.25);
        margin-bottom: 12px;
    }

    .aspect-title {
        font-size: 17px;
        font-weight: 700;
    }

    .aspect-detail {
        font-size: 13px;
        margin-top: 5px;
    }

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# LOAD ENGINE
# ============================================================

@st.cache_resource
def load_aggregator() -> ReviewAggregator:
    return ReviewAggregator(DATA_PATH)


@st.cache_resource
def load_ollama_client() -> OllamaABSAClient:
    return OllamaABSAClient()


aggregator = load_aggregator()
ollama_client = load_ollama_client()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🏨 Voice of Customer")

    st.caption(
        "AI-Powered Voice of Customer Intelligence "
        "untuk industri perhotelan."
    )

    st.divider()

    st.markdown("### 📂 Sumber Data")

    st.info(
        "PoC saat ini menggunakan dataset "
        "IndoNLU TERMA.\n\n"
        "Data review hotel Ciputra aktual "
        "belum digunakan."
    )

    available_hotels = aggregator.get_available_hotels()

    if available_hotels:

        hotel_options = ["Semua Hotel"] + available_hotels

        selected_hotel = st.selectbox(
            "Pilih Hotel / Sumber",
            hotel_options,
        )

        active_aggregator = aggregator.filter_by_hotel(
            selected_hotel
        )

    else:

        selected_hotel = "Dataset TERMA"
        active_aggregator = aggregator

        st.caption(
            "Dataset belum memiliki metadata hotel."
        )

    st.divider()

    st.markdown("### 🤖 Teknologi")

    st.write("**Model:** Qwen3:8B")
    st.write("**Inference:** Ollama Local")
    st.write("**Metode:** Aspect-Based Sentiment Analysis")
    st.write("**Dataset:** IndoNLU TERMA")

    st.divider()

    st.caption(
        "Proof of Concept — Ciputra Group"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-header">
        <div class="main-title">
            🏨 AI-Powered Voice of Customer Intelligence
        </div>
        <div class="main-subtitle">
            Proof of Concept · Hospitality · Ciputra Group
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================

tab_dashboard, tab_live = st.tabs(
    [
        "📊 Dashboard Inteligensi Pelanggan",
        "🔍 Analisis Ulasan Langsung",
    ]
)


# ============================================================
# TAB 1 — DASHBOARD
# ============================================================

with tab_dashboard:

    # --------------------------------------------------------
    # KPI
    # --------------------------------------------------------

    kpis = active_aggregator.calculate_kpis()

    st.subheader("📌 Ringkasan Eksekutif")

    executive_summary = (
        active_aggregator.generate_executive_summary_text()
    )

    st.info(
        f"💡 **Insight Utama**\n\n"
        f"{executive_summary}"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Ulasan",
            value=f"{kpis['total_reviews']:,}",
        )

    with col2:
        st.metric(
            label="Aspek Bersentimen Positif",
            value=f"{kpis['positive_aspect_percentage']:.1f}%",
        )

    with col3:
        st.metric(
            label="Prioritas Perbaikan #1",
            value=kpis["top_priority"],
        )

    with col4:
        st.metric(
            label="Keunggulan Utama",
            value=kpis["top_strength"],
        )

    st.divider()

    # --------------------------------------------------------
    # PRIORITAS & STRENGTH
    # --------------------------------------------------------

    col_left, col_right = st.columns(2)

    # ========================================================
    # PRIORITAS
    # ========================================================

    with col_left:

        st.subheader("🔥 Prioritas Perbaikan")

        st.caption(
            "Aspek yang memiliki kombinasi volume penyebutan "
            "dan proporsi keluhan negatif paling tinggi."
        )

        priorities = active_aggregator.get_top_priorities(
            top_n=5
        )

        if not priorities:

            st.success(
                "Belum terdapat aspek negatif yang cukup "
                "untuk membentuk prioritas."
            )

        else:

            for rank, item in enumerate(
                priorities,
                start=1,
            ):

                with st.container(border=True):

                    st.markdown(
                        f"### #{rank} {item['category']}"
                    )

                    st.caption(
                        f"{item['total_mentions']} penyebutan · "
                        f"{item['negative_count']} keluhan negatif"
                    )

                    c1, c2 = st.columns(2)

                    with c1:

                        st.metric(
                            "Proporsi Negatif",
                            f"{item['negative_ratio']}%",
                        )

                    with c2:

                        st.metric(
                            "Skor Prioritas",
                            f"{item['priority_score']:.1f}",
                        )


    # ========================================================
    # STRENGTH
    # ========================================================

    with col_right:

        st.subheader("🟢 Keunggulan Layanan")

        st.caption(
            "Aspek yang memiliki proporsi sentimen positif "
            "tinggi dengan jumlah penyebutan yang memadai."
        )

        strengths = active_aggregator.get_top_strengths(
            top_n=5
        )

        if not strengths:

            st.info(
                "Belum terdapat cukup data untuk "
                "menentukan keunggulan layanan."
            )

        else:

            for rank, item in enumerate(
                strengths,
                start=1,
            ):

                with st.container(border=True):

                    st.markdown(
                        f"### #{rank} {item['category']}"
                    )

                    st.caption(
                        f"{item['total_mentions']} penyebutan · "
                        f"{item['positive_count']} sentimen positif"
                    )

                    st.metric(
                        "Proporsi Positif",
                        f"{item['positive_ratio']:.1f}%",
                    )

    st.divider()

    # --------------------------------------------------------
    # SENTIMENT CHART
    # --------------------------------------------------------

    st.subheader("📊 Sentimen Berdasarkan Aspek")

    st.caption(
        "Distribusi sentimen positif, netral, dan negatif "
        "berdasarkan aspek yang terdeteksi oleh AI."
    )

    df_summary = (
        active_aggregator.get_aspect_summary()
    )

    if df_summary.empty:

        st.info(
            "Belum ada data aspek yang dapat divisualisasikan."
        )

    else:

        chart_df = df_summary.sort_values(
            "total_mentions",
            ascending=True,
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=chart_df["category"],
                x=chart_df["positive_count"],
                name="Positif",
                orientation="h",
                marker_color="#22c55e",
            )
        )

        fig.add_trace(
            go.Bar(
                y=chart_df["category"],
                x=chart_df["neutral_count"],
                name="Netral",
                orientation="h",
                marker_color="#eab308",
            )
        )

        fig.add_trace(
            go.Bar(
                y=chart_df["category"],
                x=chart_df["negative_count"],
                name="Negatif",
                orientation="h",
                marker_color="#ef4444",
            )
        )

        fig.update_layout(
            barmode="stack",
            height=max(
                400,
                len(chart_df) * 45,
            ),
            margin=dict(
                l=20,
                r=20,
                t=30,
                b=20,
            ),
            xaxis_title="Jumlah Penyebutan",
            yaxis_title="",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.divider()

    # --------------------------------------------------------
    # EVIDENCE
    # --------------------------------------------------------

    st.subheader("🔎 Bukti dari Ulasan Pelanggan")

    st.caption(
        "Contoh ulasan yang mendukung temuan aspek."
    )

    if df_summary.empty:

        st.info(
            "Belum ada evidence yang dapat ditampilkan."
        )

    else:

        all_categories = (
            df_summary["category"]
            .tolist()
        )

        priorities = (
            active_aggregator
            .get_top_priorities(top_n=5)
        )

        priority_names = [
            item["category"]
            for item in priorities
        ]

        default_index = 0

        if priority_names:

            first_priority = priority_names[0]

            if first_priority in all_categories:

                default_index = (
                    all_categories.index(
                        first_priority
                    )
                )

        selected_aspect = st.selectbox(
            "Pilih Aspek",
            all_categories,
            index=default_index,
        )

        evidence = (
            active_aggregator
            .get_evidence(selected_aspect)
        )

        if evidence:

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "Jumlah Penyebutan",
                    evidence["total_mentions"],
                )

            with c2:

                st.metric(
                    "Keluhan Negatif",
                    evidence["negative_count"],
                )

            with c3:

                st.metric(
                    "Proporsi Negatif",
                    f"{evidence['negative_ratio']:.1f}%",
                )

            st.markdown(
                "#### Contoh Ulasan"
            )

            examples = (
                evidence.get(
                    "example_reviews",
                    [],
                )
            )

            if examples:

                for review in examples:

                    safe_review = html.escape(
                        str(review)
                    )

                    st.markdown(
                        f"""
<div class="quote-box">
    "{safe_review}"
</div>
""",
                        unsafe_allow_html=True,
                    )

            else:

                st.info(
                    "Belum ada contoh ulasan."
                )

    st.divider()

    # --------------------------------------------------------
    # TABLE
    # --------------------------------------------------------

    st.subheader("📋 Rekapitulasi Analisis Aspek")

    if df_summary.empty:

        st.info(
            "Belum ada data untuk ditampilkan."
        )

    else:

        display_df = df_summary[
            [
                "category",
                "total_mentions",
                "positive_count",
                "negative_count",
                "neutral_count",
                "positive_ratio",
                "negative_ratio",
                "priority_score",
            ]
        ].rename(
            columns={
                "category": "Kategori Aspek",
                "total_mentions": "Jumlah Penyebutan",
                "positive_count": "Positif",
                "negative_count": "Negatif",
                "neutral_count": "Netral",
                "positive_ratio": "Positif (%)",
                "negative_ratio": "Negatif (%)",
                "priority_score": "Skor Prioritas",
            }
        )

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        with st.expander(
            "ℹ️ Cara membaca Skor Prioritas"
        ):

            st.write(
                "Skor Prioritas merupakan skor perbandingan "
                "relatif antar-aspek. Skor dihitung dari "
                "jumlah penyebutan dikalikan proporsi "
                "sentimen negatif. Semakin tinggi skor, "
                "semakin layak aspek tersebut diprioritaskan "
                "untuk evaluasi."
            )

            st.caption(
                "Catatan: skor ini bukan ukuran kepuasan "
                "pelanggan absolut dan tidak menunjukkan "
                "hubungan sebab-akibat."
            )


# ============================================================
# TAB 2 — LIVE REVIEW ANALYZER
# ============================================================

with tab_live:

    st.subheader(
        "🔍 Analisis Ulasan Pelanggan Secara Langsung"
    )

    st.caption(
        "Masukkan ulasan pelanggan berbahasa Indonesia. "
        "Qwen3:8B akan mengidentifikasi aspek, target, "
        "opini, dan sentimen."
    )

    default_review = (
        "Kamarnya sangat bersih dan staf resepsionis ramah, "
        "tetapi Wi-Fi di lantai 3 sangat lambat dan AC agak berisik."
    )

    user_review = st.text_area(
        "Masukkan Ulasan Pelanggan",
        value=default_review,
        height=130,
        placeholder=(
            "Contoh: Kamarnya bersih tetapi WiFi sangat lambat."
        ),
    )

    analyze_button = st.button(
        "🚀 Analisis dengan AI",
        type="primary",
        use_container_width=False,
    )

    if analyze_button:

        if not user_review.strip():

            st.error(
                "Silakan masukkan teks ulasan terlebih dahulu."
            )

        elif not ollama_client.is_available():

            st.error(
                "❌ Ollama tidak dapat diakses. "
                "Pastikan Ollama sedang berjalan."
            )

            st.code(
                "ollama serve",
                language="bash",
            )

        else:

            with st.spinner(
                "🤖 Qwen3:8B sedang menganalisis ulasan..."
            ):

                results = (
                    ollama_client
                    .analyze_review(
                        user_review
                    )
                )

            if not results:

                st.warning(
                    "Tidak ada aspek yang berhasil "
                    "diekstrak dari ulasan."
                )

                st.caption(
                    "Pastikan model Qwen3:8B tersedia "
                    "di Ollama dan teks mengandung "
                    "aspek layanan atau fasilitas."
                )

            else:

                st.success(
                    f"Analisis selesai. "
                    f"{len(results)} aspek terdeteksi."
                )

                # --------------------------------------------
                # Ringkasan sentiment
                # --------------------------------------------

                positive_count = sum(
                    1
                    for item in results
                    if item.get("sentiment")
                    == "positif"
                )

                negative_count = sum(
                    1
                    for item in results
                    if item.get("sentiment")
                    == "negatif"
                )

                neutral_count = sum(
                    1
                    for item in results
                    if item.get("sentiment")
                    == "netral"
                )

                c1, c2, c3 = st.columns(3)

                with c1:

                    st.metric(
                        "🟢 Positif",
                        positive_count,
                    )

                with c2:

                    st.metric(
                        "🔴 Negatif",
                        negative_count,
                    )

                with c3:

                    st.metric(
                        "🟡 Netral",
                        neutral_count,
                    )

                st.divider()

                # --------------------------------------------
                # HASIL ASPEK
                # --------------------------------------------

                st.subheader(
                    "🎯 Aspek yang Terdeteksi"
                )

                columns = st.columns(2)

                for index, result in enumerate(
                    results
                ):

                    category = html.escape(
                        str(
                            result.get(
                                "category",
                                "-",
                            )
                        )
                    )

                    target = html.escape(
                        str(
                            result.get(
                                "target",
                                "-",
                            )
                        )
                    )

                    opinion = html.escape(
                        str(
                            result.get(
                                "opinion",
                                "-",
                            )
                        )
                    )

                    sentiment = (
                        str(
                            result.get(
                                "sentiment",
                                "netral",
                            )
                        )
                        .lower()
                        .strip()
                    )

                    if sentiment == "positif":

                        badge = "🟢 Positif"

                    elif sentiment == "negatif":

                        badge = "🔴 Negatif"

                    else:

                        badge = "🟡 Netral"

                    with columns[index % 2]:

                        with st.container(
                            border=True
                        ):

                            st.markdown(
                                f"### {category}"
                            )

                            st.markdown(
                                f"**Target:** {target}"
                            )

                            st.markdown(
                                f'**Opini:** "{opinion}"'
                            )

                            st.markdown(
                                f"**Sentimen:** {badge}"
                            )

                # --------------------------------------------
                # INTERPRETASI
                # --------------------------------------------

                st.divider()

                st.subheader(
                    "💡 Interpretasi"
                )

                negative_aspects = [
                    item
                    for item in results
                    if item.get("sentiment")
                    == "negatif"
                ]

                positive_aspects = [
                    item
                    for item in results
                    if item.get("sentiment")
                    == "positif"
                ]

                if negative_aspects:

                    negative_names = ", ".join(
                        str(
                            item.get(
                                "category",
                                "-",
                            )
                        )
                        for item in negative_aspects
                    )

                    st.warning(
                        f"Ulasan mengindikasikan "
                        f"keluhan pada aspek: "
                        f"**{negative_names}**."
                    )

                if positive_aspects:

                    positive_names = ", ".join(
                        str(
                            item.get(
                                "category",
                                "-",
                            )
                        )
                        for item in positive_aspects
                    )

                    st.success(
                        f"Ulasan memberikan penilaian "
                        f"positif pada aspek: "
                        f"**{positive_names}**."
                    )

                if not negative_aspects and not positive_aspects:

                    st.info(
                        "Ulasan tidak menunjukkan "
                        "sentimen positif maupun negatif "
                        "yang kuat."
                    )

                # --------------------------------------------
                # JSON
                # --------------------------------------------

                with st.expander(
                    "🔧 Lihat Output JSON"
                ):

                    st.caption(
                        "Output terstruktur dari Qwen3:8B "
                        "melalui Ollama."
                    )

                    st.json(
                        {
                            "aspects": results
                        }
                    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI-Powered Voice of Customer Intelligence · "
    "Proof of Concept · Ciputra Group"
)