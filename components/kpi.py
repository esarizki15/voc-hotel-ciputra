import html

import streamlit as st


def render_kpis(kpis):

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
<div class="kpi-card">
    <div class="kpi-value">
        {kpis["total_reviews"]:,}
    </div>
    <div class="kpi-label">
        Total Ulasan
    </div>
    <div class="kpi-sub">
        Dataset PoC
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col2:

        st.markdown(
            f"""
<div class="kpi-card">
    <div class="kpi-value">
        {kpis["positive_aspect_percentage"]:.1f}%
    </div>
    <div class="kpi-label">
        Aspek Bersentimen Positif
    </div>
    <div class="kpi-sub">
        Bukan persentase tamu puas
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col3:

        value = html.escape(
            str(kpis["top_priority"])
        )

        st.markdown(
            f"""
<div class="kpi-card">
    <div class="kpi-value">
        {value}
    </div>
    <div class="kpi-label">
        Prioritas Perbaikan #1
    </div>
    <div class="kpi-sub">
        Berdasarkan skor prioritas
    </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with col4:

        value = html.escape(
            str(kpis["top_strength"])
        )

        st.markdown(
            f"""
<div class="kpi-card">
    <div class="kpi-value">
        {value}
    </div>
    <div class="kpi-label">
        Keunggulan Utama
    </div>
    <div class="kpi-sub">
        Sentimen positif dominan
    </div>
</div>
""",
            unsafe_allow_html=True,
        )