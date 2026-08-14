import html
import json
import os
import time
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from engine.aggregator import ReviewAggregator
from engine.ollama_client import OllamaABSAClient


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Voice of Customer Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = "data"
UPLOAD_DIR = "data/uploads"

DATA_PATH = "data/processed_reviews.json"

TOP_ASPECTS = 10

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>
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
.detail-card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
}
.detail-label {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    margin-top: 8px;
}
.detail-value {
    font-size: 14px;
    color: #e2e8f0;
    margin-top: 2px;
}
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
# ENGINE
# ============================================================

@st.cache_resource
def load_ollama_client():
    return OllamaABSAClient(model="qwen3:8b")


ollama_client = load_ollama_client()


# ============================================================
# SESSION STATE
# ============================================================

if "active_dataset" not in st.session_state:
    st.session_state.active_dataset = DATA_PATH

if "upload_results" not in st.session_state:
    st.session_state.upload_results = None


# ============================================================
# HELPERS
# ============================================================

def get_sentiment_badge(sentiment: str):
    sentiment = str(sentiment or "netral").strip().lower()
    if sentiment == "positif":
        return '<span class="badge-positive">🟢 Positif</span>'
    if sentiment == "negatif":
        return '<span class="badge-negative">🔴 Negatif</span>'
    return '<span class="badge-neutral">🟡 Netral</span>'


def load_active_aggregator():
    return ReviewAggregator(st.session_state.active_dataset)


def normalize_review_column(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def save_processed_reviews(results, path=DATA_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=2)


def render_aspect_details(active_aggregator, category, sentiment=None):
    details = active_aggregator.get_aspect_details(category_name=category, sentiment=sentiment)
    if not details:
        st.info("Tidak ditemukan detail review.")
        return
    if sentiment:
        if sentiment == "negatif":
            icon = "🔴"
        elif sentiment == "positif":
            icon = "🟢"
        else:
            icon = "🟡"
        st.subheader(f"{icon} Detail {category} — {sentiment.capitalize()}")
    else:
        st.subheader(f"🔎 Detail Aspek — {category}")
    st.caption(f"Ditemukan {len(details)} penyebutan.")
    grouped = {}
    for item in details:
        review_id = item.get("review_id", "-")
        if review_id not in grouped:
            grouped[review_id] = []
        grouped[review_id].append(item)
    for review_id, items in grouped.items():
        review_text = str(items[0].get("review_text", "-"))
        safe_text = html.escape(review_text)
        with st.expander(f"📝 Review #{review_id} · {len(items)} penyebutan"):
            st.markdown(f'<div class="quote-box">"{safe_text}"</div>', unsafe_allow_html=True)
            st.markdown("#### Aspek yang Terdeteksi")
            for item in items:
                target = html.escape(str(item.get("target", "-")))
                opinion = html.escape(str(item.get("opinion", "-")))
                sentiment_value = str(item.get("sentiment", "netral")).strip().lower()
                badge = get_sentiment_badge(sentiment_value)
                st.markdown(f"""
<div class="detail-card">
    <div class="detail-label">Target</div>
    <div class="detail-value">{target}</div>
    <div class="detail-label">Opinion</div>
    <div class="detail-value">"{opinion}"</div>
    <div class="detail-label">Sentiment</div>
    <div style="margin-top:5px;">{badge}</div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🏨 Voice of Customer")
    st.caption("AI-Powered Voice of Customer Intelligence untuk industri perhotelan.")
    st.divider()
    st.markdown("### 📂 Dataset")
    dataset_options = ["Dataset Aktif", "Upload Dataset Baru"]
    dataset_mode = st.radio("Sumber Data", dataset_options, key="dataset_mode")
    if dataset_mode == "Upload Dataset Baru":
        st.markdown("#### Upload Review")
        uploaded_file = st.file_uploader(
            "CSV / Excel",
            type=["csv", "xlsx", "xls"],
            help="Upload dataset review pelanggan dalam format CSV atau Excel.",
        )
        if uploaded_file:
            try:
                if uploaded_file.name.lower().endswith(".csv"):
                    df_upload = pd.read_csv(uploaded_file)
                else:
                    df_upload = pd.read_excel(uploaded_file)
                st.success(f"{len(df_upload):,} baris berhasil dibaca.")
                st.markdown("##### Pilih Kolom Review")
                review_columns = df_upload.columns.tolist()
                if not review_columns:
                    st.error("Dataset tidak memiliki kolom.")
                else:
                    default_review_index = 0
                    for i, column in enumerate(review_columns):
                        column_lower = str(column).lower()
                        if any(keyword in column_lower for keyword in ["review", "ulasan", "comment", "text", "content"]):
                            default_review_index = i
                            break
                    selected_review_column = st.selectbox("Kolom Review", review_columns, index=default_review_index)
                    st.markdown("##### Preview")
                    st.dataframe(df_upload[[selected_review_column]].head(5), use_container_width=True, hide_index=True)
                    st.caption(f"Total review: {len(df_upload):,}")
                    process_button = st.button("🚀 Mulai Analisis AI", type="primary", use_container_width=True)
                    if process_button:
                        if not ollama_client.is_available():
                            st.error("❌ Ollama tidak dapat diakses.")
                            st.code("ollama serve", language="bash")
                        elif not ollama_client.is_model_available():
                            st.error("❌ Model Qwen3:8B belum tersedia.")
                            st.code("ollama pull qwen3:8b", language="bash")
                        else:
                            total_rows = len(df_upload)
                            processed_results = []
                            progress_bar = st.progress(0)
                            progress_text = st.empty()
                            status_text = st.empty()
                            success_count = 0
                            error_count = 0
                            empty_count = 0
                            start_time = time.time()
                            for index, row in df_upload.iterrows():
                                review_id = index + 1
                                review_text = normalize_review_column(row[selected_review_column])
                                progress_text.write(f"Memproses review {review_id:,} dari {total_rows:,}...")
                                if not review_text:
                                    processed_results.append({
                                        "review_id": review_id,
                                        "review_text": "",
                                        "aspects": [],
                                        "status": "empty",
                                        "error": "Review kosong.",
                                    })
                                    empty_count += 1
                                else:
                                    try:
                                        aspects = ollama_client.analyze_review(review_text)
                                        processed_results.append({
                                            "review_id": review_id,
                                            "review_text": review_text,
                                            "aspects": aspects,
                                            "status": "success",
                                            "error": None,
                                        })
                                        success_count += 1
                                    except Exception as error:
                                        processed_results.append({
                                            "review_id": review_id,
                                            "review_text": review_text,
                                            "aspects": [],
                                            "status": "error",
                                            "error": str(error),
                                        })
                                        error_count += 1
                                save_processed_reviews(processed_results, DATA_PATH)
                                progress = review_id / total_rows
                                progress_bar.progress(progress)
                                elapsed = time.time() - start_time
                                if review_id:
                                    avg_time = elapsed / review_id
                                    remaining = total_rows - review_id
                                    estimated = avg_time * remaining
                                else:
                                    estimated = 0
                                status_text.caption(f"✓ Berhasil: {success_count:,} · Kosong: {empty_count:,} · Error: {error_count:,} · Estimasi tersisa: {estimated:.0f} detik")
                            progress_bar.progress(1.0)
                            save_processed_reviews(processed_results, DATA_PATH)
                            st.session_state.active_dataset = DATA_PATH
                            st.session_state.upload_results = {
                                "total": total_rows,
                                "success": success_count,
                                "empty": empty_count,
                                "error": error_count,
                            }
                            st.success("🎉 Analisis dataset selesai.")
                            st.rerun()
            except Exception as error:
                st.error("Gagal membaca file.")
                st.exception(error)
    st.divider()
    active_dataset = st.session_state.active_dataset
    if os.path.exists(active_dataset):
        st.success("Dataset aktif tersedia.")
        st.caption(active_dataset)
    else:
        st.warning("Dataset aktif belum tersedia.")
    st.divider()
    st.markdown("### 🤖 Teknologi")
    st.write("**Model:** Qwen3:8B")
    st.write("**Inference:** Ollama Local")
    st.write("**Metode:** Aspect-Based Sentiment Analysis")
    st.divider()
    st.caption("Proof of Concept — Ciputra Group")


# ============================================================
# LOAD ACTIVE DATASET
# ============================================================

active_aggregator = load_active_aggregator()


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
# DASHBOARD
# ============================================================

with tab_dashboard:
    df_summary = active_aggregator.get_aspect_summary()
    kpis = active_aggregator.calculate_kpis()
    st.subheader("📌 Ringkasan Eksekutif")
    executive_summary = active_aggregator.generate_executive_summary_text()
    st.markdown(f"""
<div class="insight-card">
    <div class="insight-title">💡 Ringkasan Insight Eksekutif</div>
    <div class="insight-body">{html.escape(executive_summary)}</div>
</div>
""", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{kpis["total_reviews"]:,}</div>
    <div class="kpi-label">Total Ulasan</div>
    <div class="kpi-sub">Dataset aktif</div>
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
        st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{html.escape(str(kpis["top_priority"]))}</div>
    <div class="kpi-label">Prioritas Perbaikan #1</div>
    <div class="kpi-sub">Berdasarkan skor prioritas</div>
</div>
""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
<div class="kpi-card">
    <div class="kpi-value">{html.escape(str(kpis["top_strength"]))}</div>
    <div class="kpi-label">Keunggulan Utama</div>
    <div class="kpi-sub">Sentimen positif dominan</div>
</div>
""", unsafe_allow_html=True)
    st.divider()
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("🔥 Prioritas Perbaikan")
        priorities = active_aggregator.get_top_priorities(top_n=5)
        if not priorities:
            st.success("Belum terdapat prioritas perbaikan.")
        else:
            for rank, item in enumerate(priorities, start=1):
                with st.container(border=True):
                    st.markdown(f"### #{rank} {item['category']}")
                    st.caption(f"{item['total_mentions']} penyebutan · {item['negative_count']} keluhan negatif")
                    c1, c2 = st.columns(2)
                    with c1:
                        st.metric("Proporsi Negatif", f"{item['negative_ratio']:.1f}%")
                    with c2:
                        st.metric("Skor Prioritas", f"{item['priority_score']:.1f}")
    with col_right:
        st.subheader("🟢 Keunggulan Layanan")
        strengths = active_aggregator.get_top_strengths(top_n=5)
        if not strengths:
            st.info("Belum terdapat cukup data.")
        else:
            for rank, item in enumerate(strengths, start=1):
                with st.container(border=True):
                    st.markdown(f"### #{rank} {item['category']}")
                    st.caption(f"{item['total_mentions']} penyebutan · {item['positive_count']} positif")
                    st.metric("Proporsi Positif", f"{item['positive_ratio']:.1f}%")
    st.divider()
    st.subheader("📊 Sentimen Berdasarkan Aspek")
    st.caption("Klik bagian grafik untuk melihat detail review.")
    if df_summary.empty:
        st.info("Belum ada data aspek.")
    else:
        chart_df = df_summary.sort_values("total_mentions", ascending=False).head(TOP_ASPECTS).sort_values("total_mentions", ascending=True).reset_index(drop=True)
        fig = go.Figure()
        for sentiment, label, color in [
            ("positive_count", "Positif", "#22c55e"),
            ("neutral_count", "Netral", "#eab308"),
            ("negative_count", "Negatif", "#ef4444"),
        ]:
            fig.add_trace(go.Bar(
                y=chart_df["category"],
                x=chart_df[sentiment],
                name=label,
                orientation="h",
                marker_color=color,
                customdata=[[row["category"], label.lower()] for _, row in chart_df.iterrows()],
                hovertemplate=f"<b>%{{y}}</b><br>Sentimen: {label}<br>Jumlah: %{{x}}<br><extra>Klik untuk detail</extra>",
            ))
        fig.update_layout(
            barmode="stack",
            height=max(450, len(chart_df) * 55),
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis_title="Jumlah Penyebutan",
            yaxis_title="",
        )
        chart_event = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="sentiment_chart")
        selected_category = None
        selected_sentiment = None
        try:
            if chart_event:
                points = chart_event.selection.points
                if points:
                    point = points[0]
                    customdata = point.get("customdata")
                    if customdata:
                        selected_category = customdata[0]
                        selected_sentiment = customdata[1]
        except Exception:
            pass
        if selected_category and selected_sentiment:
            st.divider()
            render_aspect_details(active_aggregator, selected_category, selected_sentiment)
    st.divider()
    st.subheader("🔎 Detail Evidence Aspek")
    if df_summary.empty:
        st.info("Belum ada evidence.")
    else:
        categories = df_summary.sort_values("total_mentions", ascending=False)["category"].tolist()
        selected_aspect = st.selectbox("Pilih Aspek", categories, key="manual_aspect")
        evidence = active_aggregator.get_evidence(selected_aspect)
        if evidence:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Jumlah Penyebutan", evidence["total_mentions"])
            with c2:
                st.metric("Keluhan Negatif", evidence["negative_count"])
            with c3:
                st.metric("Proporsi Negatif", f"{evidence['negative_ratio']:.1f}%")
            render_aspect_details(active_aggregator, selected_aspect)
    st.divider()
    st.subheader("📋 Rekapitulasi Analisis Aspek")
    if not df_summary.empty:
        display_df = df_summary[[
            "category", "total_mentions", "positive_count", "negative_count",
            "neutral_count", "positive_ratio", "negative_ratio", "priority_score"
        ]].copy().rename(columns={
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
    else:
        st.info("Belum ada data.")


# ============================================================
# LIVE ANALYZER
# ============================================================

with tab_live:
    st.subheader("🔍 Analisis Ulasan Pelanggan Secara Langsung")
    st.caption("Masukkan satu review untuk dianalisis oleh Qwen3:8B.")
    user_review = st.text_area(
        "Masukkan Ulasan Pelanggan",
        value="Kamarnya sangat bersih dan staf resepsionis ramah, tetapi Wi-Fi sangat lambat dan AC agak berisik.",
        height=130,
    )
    analyze_button = st.button("🚀 Analisis dengan AI", type="primary")
    if analyze_button:
        if not user_review.strip():
            st.error("Review tidak boleh kosong.")
        elif not ollama_client.is_available():
            st.error("Ollama tidak dapat diakses.")
            st.code("ollama serve", language="bash")
        else:
            with st.spinner("🤖 Qwen3:8B menganalisis..."):
                try:
                    results = ollama_client.analyze_review(user_review)
                except Exception as error:
                    st.error("Analisis gagal.")
                    st.exception(error)
                    results = []
            if results:
                st.success(f"{len(results)} aspek terdeteksi.")
                positive = sum(1 for item in results if item["sentiment"] == "positif")
                negative = sum(1 for item in results if item["sentiment"] == "negatif")
                neutral = sum(1 for item in results if item["sentiment"] == "netral")
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("🟢 Positif", positive)
                with c2:
                    st.metric("🔴 Negatif", negative)
                with c3:
                    st.metric("🟡 Netral", neutral)
                st.divider()
                st.subheader("🎯 Aspek Terdeteksi")
                columns = st.columns(2)
                for index, result in enumerate(results):
                    category = html.escape(str(result.get("category", "-")))
                    target = html.escape(str(result.get("target", "-")))
                    opinion = html.escape(str(result.get("opinion", "-")))
                    sentiment = str(result.get("sentiment", "netral")).strip().lower()
                    badge = get_sentiment_badge(sentiment)
                    with columns[index % 2]:
                        with st.container(border=True):
                            st.markdown(f"### {category}")
                            st.markdown(f"**Target:** {target}")
                            st.markdown(f'**Opinion:** "{opinion}"')
                            st.markdown(f"**Sentiment:** {badge}", unsafe_allow_html=True)
                st.divider()
                with st.expander("🔧 Lihat Output JSON"):
                    st.json({"aspects": results})
            else:
                st.warning("Tidak ada aspek yang berhasil ditemukan.")


# ============================================================
# FOOTER
# ============================================================

st.divider()
st.caption("AI-Powered Voice of Customer Intelligence · Proof of Concept · Ciputra Group")