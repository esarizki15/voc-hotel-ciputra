import html
import pandas as pd
import streamlit as st


def render_kpis(kpis, active_aggregator=None):

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
        value = html.escape(str(kpis["top_priority"]))

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
        value = html.escape(str(kpis["top_strength"]))

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

    # Preview Dataset Ulasan Mentah
    if (
        active_aggregator
        and hasattr(active_aggregator, "reviews")
        and active_aggregator.reviews
    ):
        # Penambahan Spacing / Margin Top 18px
        st.markdown(
            "<div style='margin-top: 18px;'></div>",
            unsafe_allow_html=True,
        )

        with st.expander("👁️ Preview Raw Data Ulasan Pelanggan", expanded=False):
            reviews_data = []
            for item in active_aggregator.reviews:
                r_id = item.get("review_id") or item.get("id") or "-"
                r_hotel = item.get("hotel") or item.get("hotel_name") or "N/A"
                r_text = item.get("review_text") or item.get("text") or ""
                aspects = (
                    item.get("aspects") or item.get("aspect_sentiments") or []
                )

                reviews_data.append(
                    {
                        "Review ID": r_id,
                        "Nama Hotel": r_hotel,
                        "Teks Review Pelanggan": r_text,
                        "Aspek Terdeteksi": (
                            len(aspects) if isinstance(aspects, list) else 0
                        ),
                    }
                )

            df_reviews = pd.DataFrame(reviews_data)

            search_query = st.text_input(
                "🔍 Cari Ulasan berdasarkan kata kunci atau Review ID:",
                key="kpi_review_search",
            )

            if search_query:
                df_reviews = df_reviews[
                    df_reviews["Teks Review Pelanggan"].str.contains(
                        search_query, case=False, na=False
                    )
                    | df_reviews["Review ID"]
                    .astype(str)
                    .str.contains(search_query, case=False, na=False)
                ]

            st.dataframe(
                df_reviews,
                use_container_width=True,
                hide_index=True,
                height=300,
            )