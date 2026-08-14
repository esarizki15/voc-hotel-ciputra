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

TOP_ASPECTS = 10


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>
    /* ========================================================
       HEADER
       ======================================================== */
    .header-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-bottom: 2px solid #38bdf8;
        padding: 22px 28px;
        border-radius: 12px;
        margin-bottom: 22px;
    }
    .header-title {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 6px;
    }
    /* ========================================================
       INSIGHT
       ======================================================== */
    .insight-card {
        background-color: #1e293b;
        border-left: 5px solid #0ea5e9;
        padding: 18px 22px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .insight-title {
        color: #38bdf8;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .insight-body {
        color: #e2e8f0;
        font-size: 15px;
        line-height: 1.6;
    }
    /* ========================================================
       KPI
       ======================================================== */
    .kpi-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        min-height: 120px;
    }
    .kpi-value {
        font-size: 30px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-label {
        font-size: 13px;
        color: #94a3b8;
        font-weight: 600;
    }
    .kpi-sub {
        font-size: 11px;
        color: #64748b;
        margin-top: 5px;
    }
    /* ========================================================
       QUOTE
       ======================================================== */
    .quote-box {
        background-color: #0f172a;
        border-left: 4px solid #ef4444;
        padding: 12px 18px;
        margin-top: 10px;
        border-radius: 0 8px 8px 0;
        font-style: italic;
        color: #cbd5e1;
        font-size: 14px;
    }
    /* ========================================================
       DETAIL CARD
       ======================================================== */
    .detail-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 18px;
        margin-bottom: 12px;
    }
    .detail-title {
        font-size: 16px;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 8px;
    }
    .detail-label {
        font-size: 12px;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        margin-top: 10px;
    }
    .detail-value {
        font-size: 14px;
        color: #e2e8f0;
        margin-top: 2px;
    }
    /* ========================================================
       ASPECT ITEM
       ======================================================== */
    .aspect-item {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 10px 12px;
        margin-top: 8px;
    }
    .aspect-name {
        font-size: 14px;
        font-weight: 700;
        color: #f8fafc;
    }
    .aspect-meta {
        font-size: 13px;
        color: #cbd5e1;
        margin-top: 3px;
    }
    /* ========================================================
       BADGE
       ======================================================== */
    .badge-positive {
        display: inline-block;
        background-color: rgba(34, 197, 94, 0.15);
        color: #86efac;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-negative {
        display: inline-block;
        background-color: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .badge-neutral {
        display: inline-block;
        background-color: rgba(234, 179, 8, 0.15);
        color: #fde047;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
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
# HELPER
# ============================================================

def normalize_sentiment(sentiment: str) -> str:
    return str(sentiment or "netral").strip().lower()


def get_sentiment_badge(sentiment: str) -> str:
    sentiment = normalize_sentiment(sentiment)
    if sentiment == "positif":
        return '<span class="badge-positive">🟢 Positif</span>'
    if sentiment == "negatif":
        return '<span class="badge-negative">🔴 Negatif</span>'
    return '<span class="badge-neutral">🟡 Netral</span>'


def get_sentiment_icon(sentiment: str) -> str:
    sentiment = normalize_sentiment(sentiment)
    if sentiment == "positif":
        return "🟢"
    if sentiment == "negatif":
        return "🔴"
    return "🟡"


def group_details_by_review(details):
    """
    Mengelompokkan hasil ABSA berdasarkan review_id.
    Sebelumnya: 1 sentiment/aspect = 1 evidence
    Sekarang: 1 review = 1 evidence
    Semua aspek yang berasal dari review yang sama akan digabungkan ke dalam satu review.
    """
    grouped = {}
    for item in details:
        review_id = str(item.get("review_id", "-"))
        if review_id not in grouped:
            grouped[review_id] = {
                "review_id": review_id,
                "review_text": item.get("review_text", "-"),
                "aspects": [],
            }
        grouped[review_id]["aspects"].append({
            "category": item.get("category", "-"),
            "target": item.get("target", "-"),
            "opinion": item.get("opinion", "-"),
            "sentiment": normalize_sentiment(item.get("sentiment", "netral")),
        })
    return list(grouped.values())


def render_grouped_review_details(details, title="🧾 Evidence Review"):
    """Render evidence yang sudah dikelompokkan berdasarkan review."""
    grouped_reviews = group_details_by_review(details)
    if not grouped_reviews:
        st.info("Tidak ditemukan evidence review.")
        return
    st.markdown(f"### {title}")
    st.caption(f"{len(grouped_reviews)} review unik ditemukan.")
    for index, review in enumerate(grouped_reviews, start=1):
        review_id = html.escape(str(review.get("review_id", "-")))
        review_text = html.escape(str(review.get("review_text", "-")))
        aspects = review.get("aspects", [])
        sentiment_counts = {"positif": 0, "negatif": 0, "netral": 0}
        for aspect in aspects:
            sentiment = normalize_sentiment(aspect.get("sentiment", "netral"))
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
        sentiment_badges = []
        if sentiment_counts["positif"]:
            sentiment_badges.append(f"🟢 {sentiment_counts['positif']} positif")
        if sentiment_counts["negatif"]:
            sentiment_badges.append(f"🔴 {sentiment_counts['negatif']} negatif")
        if sentiment_counts["netral"]:
            sentiment_badges.append(f"🟡 {sentiment_counts['netral']} netral")
        sentiment_summary = " · ".join(sentiment_badges)
        with st.expander(f"Review #{review_id} · {len(aspects)} temuan · {sentiment_summary}", expanded=index == 1):
            st.markdown(f"""
<div class="detail-card">
    <div class="detail-title">📝 Review #{review_id}</div>
    <div class="detail-label">Review Pelanggan</div>
    <div class="quote-box">"{review_text}"</div>
</div>
""", unsafe_allow_html=True)
            st.markdown("#### 🎯 Temuan AI")
            for aspect in aspects:
                category = html.escape(str(aspect.get("category", "-")))
                target = html.escape(str(aspect.get("target", "-")))
                opinion = html.escape(str(aspect.get("opinion", "-")))
                sentiment = normalize_sentiment(aspect.get("sentiment", "netral"))
                badge = get_sentiment_badge(sentiment)
                st.markdown(f"""
<div class="aspect-item">
    <div class="aspect-name">{get_sentiment_icon(sentiment)} {category}</div>
    <div class="aspect-meta"><b>Target:</b> {target}</div>
    <div class="aspect-meta"><b>Opinion:</b> "{opinion}"</div>
    <div style="margin-top:6px;">{badge}</div>
</div>
""", unsafe_allow_html=True)


def render_aspect_details(active_aggregator, category: str, sentiment: str | None = None):
    """Menampilkan evidence berdasarkan aspek + optional sentiment."""
    details = active_aggregator.get_aspect_details(category_name=category, sentiment=sentiment)
    if not details:
        st.info("Tidak ditemukan detail review untuk kombinasi aspek dan sentimen tersebut.")
        return
    if sentiment:
        sentiment = normalize_sentiment(sentiment)
        sentiment_label = sentiment.capitalize()
        icon = get_sentiment_icon(sentiment)
        st.subheader(f"{icon} Detail {category} — {sentiment_label}")
    else:
        st.subheader(f"🔎 Detail Aspek — {category}")
    grouped_reviews = group_details_by_review(details)
    st.caption(f"{len(details)} penyebutan dari {len(grouped_reviews)} review unik.")
    positive_count = sum(1 for item in details if normalize_sentiment(item.get("sentiment", "netral")) == "positif")
    negative_count = sum(1 for item in details if normalize_sentiment(item.get("sentiment", "netral")) == "negatif")
    neutral_count = sum(1 for item in details if normalize_sentiment(item.get("sentiment", "netral")) == "netral")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🟢 Positif", positive_count)
    with c2:
        st.metric("🔴 Negatif", negative_count)
    with c3:
        st.metric("🟡 Netral", neutral_count)
    render_grouped_review_details(details, title="🧾 Evidence Review")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🏨 Voice of Customer")
    st.caption("AI-Powered Voice of Customer Intelligence untuk industri perhotelan.")
    st.divider()
    st.markdown("### 📂 Sumber Data")
    st.info("PoC saat ini menggunakan dataset IndoNLU TERMA.\n\nData review hotel Ciputra aktual belum digunakan.")
    available_hotels = aggregator.get_available_hotels()
    if available_hotels:
        hotel_options = ["Semua Hotel"] + available_hotels
        selected_hotel = st.selectbox("Pilih Hotel / Sumber", hotel_options)
        active_aggregator = aggregator.filter_by_hotel(selected_hotel)
    else:
        selected_hotel = "Dataset TERMA"
        active_aggregator = aggregator
        st.caption("Dataset belum memiliki metadata hotel.")
    st.divider()
    st.markdown("### 🤖 Teknologi")
    st.write("**Model:** Qwen3:8B")
    st.write("**Inference:** Ollama Local")
    st.write("**Metode:** Aspect-Based Sentiment Analysis")
    st.write("**Dataset:** IndoNLU TERMA")
    st.divider()
    st.caption("Proof of Concept — Ciputra Group")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
<div class="header-container">
    <div class="header-title">🏨 AI-Powered Voice of Customer Intelligence</div>
    <div class="header-subtitle">Proof of Concept · Hospitality · Ciputra Group</div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# TABS
# ============================================================

tab_dashboard, tab_live = st.tabs([
    "📊 Dashboard Inteligensi Pelanggan",
    "🔍 Analisis Ulasan Langsung",
])


# ============================================================
# TAB 1 — DASHBOARD
# ============================================================

with tab_dashboard:
    df_summary = active_aggregator.get_aspect_summary()
    kpis = active_aggregator.calculate_kpis()
    st.subheader("📌 Ringkasan Eksekutif")
    executive_summary = active_aggregator.generate_executive_summary_text()
    safe_summary = html.escape(executive_summary)
    st.markdown(f"""
<div class="insight-card">
    <div class="insight-title">💡 Ringkasan Insight Eksekutif</div>
    <div class="insight-body">{safe_summary}</div>
</div>
""", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{kpis["total_reviews"]:,}</div>
    <div class="kpi-label">Total Ulasan</div>
    <div class="kpi-sub">Dataset PoC</div>
</div>
""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{kpis["positive_aspect_percentage"]:.1f}%</div>
    <div class="kpi-label">Aspek Bersentimen Positif</div>
    <div class="kpi-sub">Bukan persentase tamu puas</div>
</div>
""", unsafe_allow_html=True)
    with col3:
        top_priority = html.escape(str(kpis["top_priority"]))
        st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{top_priority}</div>
    <div class="kpi-label">Prioritas Perbaikan #1</div>
    <div class="kpi-sub">Berdasarkan skor prioritas</div>
</div>
""", unsafe_allow_html=True)
    with col4:
        top_strength = html.escape(str(kpis["top_strength"]))
        st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{top_strength}</div>
    <div class="kpi-label">Keunggulan Utama</div>
    <div class="kpi-sub">Sentimen positif dominan</div>
</div>
""", unsafe_allow_html=True)
    st.divider()
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("🔥 Prioritas Perbaikan")
        st.caption("Aspek dengan kombinasi volume penyebutan dan proporsi sentimen negatif yang tinggi.")
        priorities = active_aggregator.get_top_priorities(top_n=5)
        if not priorities:
            st.success("Belum terdapat aspek negatif yang cukup untuk membentuk prioritas.")
        else:
            for rank, item in enumerate(priorities, start=1):
                with st.container(border=True):
                    st.markdown(f"### #{rank} {item['category']}")
                    st.caption(f"{item['total_mentions']} penyebutan · {item['negative_count']} keluhan negatif")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Proporsi Negatif", f"{item['negative_ratio']}%")
                    with c2:
                        st.metric("Skor Prioritas", f"{item['priority_score']:.1f}")
    with col_right:
        st.subheader("🟢 Keunggulan Layanan")
        st.caption("Aspek dengan proporsi sentimen positif tinggi dan jumlah penyebutan yang memadai.")
        strengths = active_aggregator.get_top_strengths(top_n=5)
        if not strengths:
            st.info("Belum terdapat cukup data untuk menentukan keunggulan layanan.")
        else:
            for rank, item in enumerate(strengths, start=1):
                with st.container(border=True):
                    st.markdown(f"### #{rank} {item['category']}")
                    st.caption(f"{item['total_mentions']} penyebutan · {item['positive_count']} sentimen positif")
                    st.metric("Proporsi Positif", f"{item['positive_ratio']:.1f}%")
    st.divider()
    st.subheader("📊 Sentimen Berdasarkan Aspek")
    st.caption(f"Menampilkan {TOP_ASPECTS} aspek dengan jumlah penyebutan tertinggi. Klik bagian grafik untuk melihat detail review yang membentuk angka tersebut.")
    if df_summary.empty:
        st.info("Belum ada data aspek untuk divisualisasikan.")
    else:
        chart_df = df_summary.sort_values("total_mentions", ascending=False).head(TOP_ASPECTS).sort_values("total_mentions", ascending=True).reset_index(drop=True)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=chart_df["category"],
            x=chart_df["positive_count"],
            name="Positif",
            orientation="h",
            marker_color="#22c55e",
            customdata=[[row["category"], "positif"] for _, row in chart_df.iterrows()],
            hovertemplate="<b>%{y}</b><br>Sentimen: Positif<br>Jumlah: %{x}<br><extra>Klik untuk detail</extra>",
        ))
        fig.add_trace(go.Bar(
            y=chart_df["category"],
            x=chart_df["neutral_count"],
            name="Netral",
            orientation="h",
            marker_color="#eab308",
            customdata=[[row["category"], "netral"] for _, row in chart_df.iterrows()],
            hovertemplate="<b>%{y}</b><br>Sentimen: Netral<br>Jumlah: %{x}<br><extra>Klik untuk detail</extra>",
        ))
        fig.add_trace(go.Bar(
            y=chart_df["category"],
            x=chart_df["negative_count"],
            name="Negatif",
            orientation="h",
            marker_color="#ef4444",
            customdata=[[row["category"], "negatif"] for _, row in chart_df.iterrows()],
            hovertemplate="<b>%{y}</b><br>Sentimen: Negatif<br>Jumlah: %{x}<br><extra>Klik untuk detail</extra>",
        ))
        fig.update_layout(
            barmode="stack",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f8fafc"),
            xaxis=dict(title="Jumlah Penyebutan", gridcolor="#334155"),
            yaxis=dict(title=""),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=max(450, len(chart_df) * 55),
            margin=dict(l=20, r=20, t=40, b=20),
        )
        chart_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="sentiment_chart")
        selected_category = None
        selected_sentiment = None
        try:
            if chart_event is not None:
                points = chart_event.selection.points
                if points:
                    selected_point = points[0]
                    customdata = selected_point.get("customdata")
                    if customdata and len(customdata) >= 2:
                        selected_category = str(customdata[0])
                        selected_sentiment = str(customdata[1]).strip().lower()
        except Exception:
            selected_category = None
            selected_sentiment = None
        if selected_category and selected_sentiment:
            st.divider()
            render_aspect_details(active_aggregator, selected_category, selected_sentiment)
        st.caption(f"Total kategori/aspek yang terdeteksi: {len(df_summary)}. Grafik dibatasi ke {min(TOP_ASPECTS, len(df_summary))} aspek teratas.")
    st.divider()
    st.subheader("🔎 Detail Evidence Aspek")
    st.caption("Pilih aspek untuk melihat seluruh review yang berkaitan dengan aspek tersebut.")
    if df_summary.empty:
        st.info("Belum ada evidence.")
    else:
        all_categories = df_summary.sort_values("total_mentions", ascending=False)["category"].tolist()
        priorities = active_aggregator.get_top_priorities(top_n=5)
        priority_names = [item["category"] for item in priorities]
        default_index = 0
        if priority_names:
            first_priority = priority_names[0]
            if first_priority in all_categories:
                default_index = all_categories.index(first_priority)
        selected_aspect = st.selectbox("Pilih Aspek", all_categories, index=default_index, key="manual_aspect_selector")
        evidence = active_aggregator.get_evidence(selected_aspect)
        if evidence:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Jumlah Penyebutan", evidence["total_mentions"])
            with c2:
                st.metric("Keluhan Negatif", evidence["negative_count"])
            with c3:
                st.metric("Proporsi Negatif", f"{evidence['negative_ratio']:.1f}%")
            all_details = active_aggregator.get_aspect_details(selected_aspect)
            if all_details:
                render_grouped_review_details(all_details, title="🧾 Detail Penyebutan")
            else:
                st.info("Tidak ada detail penyebutan yang tersedia.")
    st.divider()
    st.subheader("📋 Rekapitulasi Analisis Aspek")
    st.caption("Seluruh aspek hasil analisis AI ditampilkan pada tabel berikut.")
    if df_summary.empty:
        st.info("Belum ada data untuk ditampilkan.")
    else:
        display_df = df_summary[[
            "category", "total_mentions", "positive_count", "negative_count",
            "neutral_count", "positive_ratio", "negative_ratio", "priority_score"
        ]].copy().sort_values("total_mentions", ascending=False).rename(columns={
            "category": "Kategori Aspek",
            "total_mentions": "Jumlah Penyebutan",
            "positive_count": "Positif",
            "negative_count": "Negatif",
            "neutral_count": "Netral",
            "positive_ratio": "Positif (%)",
            "negative_ratio": "Negatif (%)",
            "priority_score": "Skor Prioritas",
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        with st.expander("ℹ️ Cara membaca Skor Prioritas"):
            st.write("Skor Prioritas merupakan skor perbandingan relatif antar-aspek. Skor dihitung dari jumlah penyebutan dikalikan proporsi sentimen negatif. Semakin tinggi skor, semakin layak aspek tersebut diprioritaskan untuk evaluasi.")
            st.caption("Catatan: skor ini bukan ukuran kepuasan pelanggan absolut dan tidak menunjukkan hubungan sebab-akibat.")


# ============================================================
# TAB 2 — LIVE REVIEW ANALYZER
# ============================================================

with tab_live:
    st.subheader("🔍 Analisis Ulasan Pelanggan Secara Langsung")
    st.caption("Masukkan ulasan pelanggan berbahasa Indonesia. Qwen3:8B akan mengidentifikasi aspek, target, opini, dan sentimen.")
    default_review = "Kamarnya sangat bersih dan staf resepsionis ramah, tetapi Wi-Fi di lantai 3 sangat lambat dan AC agak berisik."
    user_review = st.text_area(
        "Masukkan Ulasan Pelanggan",
        value=default_review,
        height=130,
        placeholder="Contoh: Kamarnya bersih tetapi WiFi sangat lambat.",
    )
    analyze_button = st.button("🚀 Analisis dengan AI", type="primary", use_container_width=False)
    if analyze_button:
        if not user_review.strip():
            st.error("Silakan masukkan teks ulasan terlebih dahulu.")
        elif not ollama_client.is_available():
            st.error("❌ Ollama tidak dapat diakses. Pastikan Ollama sedang berjalan.")
            st.code("ollama serve", language="bash")
        else:
            with st.spinner("🤖 Qwen3:8B sedang menganalisis ulasan..."):
                results = ollama_client.analyze_review(user_review)
            if not results:
                st.warning("Tidak ada aspek yang berhasil diekstrak dari ulasan.")
                st.caption("Pastikan model Qwen3:8B tersedia di Ollama dan teks mengandung aspek layanan atau fasilitas.")
            else:
                st.success(f"Analisis selesai. {len(results)} aspek terdeteksi.")
                positive_count = sum(1 for item in results if normalize_sentiment(item.get("sentiment", "")) == "positif")
                negative_count = sum(1 for item in results if normalize_sentiment(item.get("sentiment", "")) == "negatif")
                neutral_count = sum(1 for item in results if normalize_sentiment(item.get("sentiment", "")) == "netral")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("🟢 Positif", positive_count)
                with c2:
                    st.metric("🔴 Negatif", negative_count)
                with c3:
                    st.metric("🟡 Netral", neutral_count)
                st.divider()
                st.subheader("🎯 Aspek yang Terdeteksi")
                columns = st.columns(2)
                for index, result in enumerate(results):
                    category = html.escape(str(result.get("category", "-")))
                    target = html.escape(str(result.get("target", "-")))
                    opinion = html.escape(str(result.get("opinion", "-")))
                    sentiment = normalize_sentiment(result.get("sentiment", "netral"))
                    badge = get_sentiment_badge(sentiment)
                    with columns[index % 2]:
                        with st.container(border=True):
                            st.markdown(f"### {category}")
                            st.markdown(f"**Target:** {target}")
                            st.markdown(f'**Opini:** "{opinion}"')
                            st.markdown(f"**Sentimen:** {badge}", unsafe_allow_html=True)
                st.divider()
                st.subheader("💡 Interpretasi")
                negative_aspects = [item for item in results if normalize_sentiment(item.get("sentiment", "")) == "negatif"]
                positive_aspects = [item for item in results if normalize_sentiment(item.get("sentiment", "")) == "positif"]
                if negative_aspects:
                    negative_names = ", ".join(str(item.get("category", "-")) for item in negative_aspects)
                    st.warning(f"Ulasan mengindikasikan keluhan pada aspek: **{negative_names}**.")
                if positive_aspects:
                    positive_names = ", ".join(str(item.get("category", "-")) for item in positive_aspects)
                    st.success(f"Ulasan memberikan penilaian positif pada aspek: **{positive_names}**.")
                if not negative_aspects and not positive_aspects:
                    st.info("Ulasan tidak menunjukkan sentimen positif maupun negatif yang kuat.")
                with st.expander("🔧 Lihat Output JSON"):
                    st.caption("Output terstruktur dari Qwen3:8B melalui Ollama.")
                    st.json({"aspects": results})


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("AI-Powered Voice of Customer Intelligence · Proof of Concept · Ciputra Group")