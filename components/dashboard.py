import html

import streamlit as st

from components.kpi import render_kpis
from components.priority import render_priorities
from components.charts import render_sentiment_chart
from components.evidence import render_manual_evidence


def render_dashboard(
    active_aggregator,
    top_aspects: int = 10,
):

    # ========================================================
    # DATA
    # ========================================================

    df_summary = (
        active_aggregator
        .get_aspect_summary()
    )

    # ========================================================
    # KPI
    # ========================================================

    kpis = (
        active_aggregator
        .calculate_kpis()
    )

    st.subheader(
        "📌 Ringkasan Eksekutif"
    )

    executive_summary = (
        active_aggregator
        .generate_executive_summary_text()
    )

    safe_summary = html.escape(
        executive_summary
    )

    st.markdown(
        f"""
<div class="insight-card">
    <div class="insight-title">
        💡 Ringkasan Insight Eksekutif
    </div>
    <div class="insight-body">
        {safe_summary}
    </div>
</div>
""",
        unsafe_allow_html=True,
    )

    render_kpis(kpis)

    st.divider()

    # ========================================================
    # PRIORITY + STRENGTH
    # ========================================================

    render_priorities(
        active_aggregator
    )

    st.divider()

    # ========================================================
    # CHART
    # ========================================================

    render_sentiment_chart(
        active_aggregator,
        df_summary,
        top_aspects,
    )

    st.divider()

    # ========================================================
    # MANUAL EVIDENCE
    # ========================================================

    render_manual_evidence(
        active_aggregator,
        df_summary,
    )

    st.divider()

    # ========================================================
    # TABLE
    # ========================================================

    render_summary_table(
        df_summary
    )


def render_summary_table(
    df_summary,
):

    st.subheader(
        "📋 Rekapitulasi Analisis Aspek"
    )

    st.caption(
        "Seluruh aspek hasil analisis AI "
        "ditampilkan pada tabel berikut."
    )

    if df_summary.empty:

        st.info(
            "Belum ada data untuk ditampilkan."
        )

        return

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
    ].copy()

    display_df = (
        display_df
        .sort_values(
            "total_mentions",
            ascending=False,
        )
    )

    display_df = display_df.rename(
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
            "Skor Prioritas merupakan skor "
            "perbandingan relatif antar-aspek. "
            "Skor dihitung dari jumlah penyebutan "
            "dikalikan proporsi sentimen negatif. "
            "Semakin tinggi skor, semakin layak "
            "aspek tersebut diprioritaskan "
            "untuk evaluasi."
        )

        st.caption(
            "Catatan: skor ini bukan ukuran "
            "kepuasan pelanggan absolut dan "
            "tidak menunjukkan hubungan sebab-akibat."
        )