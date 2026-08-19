import streamlit as st

from utils.formatting import (
    escape_html,
    get_sentiment_badge,
    get_sentiment_icon,
    normalize_sentiment,
)


def render_aspect_details(
    active_aggregator,
    category: str,
    sentiment: str | None = None,
):

    details = (
        active_aggregator
        .get_aspect_details(
            category_name=category,
            sentiment=sentiment,
        )
    )

    if not details:

        st.info(
            "Tidak ditemukan detail review "
            "untuk kombinasi aspek dan sentimen tersebut."
        )

        return

    if sentiment:

        sentiment = normalize_sentiment(
            sentiment
        )

        icon = get_sentiment_icon(
            sentiment
        )

        st.subheader(
            f"{icon} Detail {category} — "
            f"{sentiment.capitalize()}"
        )

    else:

        st.subheader(
            f"🔎 Detail Aspek — {category}"
        )

    st.caption(
        f"Ditemukan {len(details)} penyebutan "
        f"yang sesuai dengan filter."
    )

    positive_count = sum(
        1
        for item in details
        if normalize_sentiment(
            item.get("sentiment")
        ) == "positif"
    )

    negative_count = sum(
        1
        for item in details
        if normalize_sentiment(
            item.get("sentiment")
        ) == "negatif"
    )

    neutral_count = sum(
        1
        for item in details
        if normalize_sentiment(
            item.get("sentiment")
        ) == "netral"
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

    st.markdown(
        "### 🧾 Evidence Review"
    )

    for index, item in enumerate(
        details,
        start=1,
    ):

        review_id = escape_html(
            item.get("review_id")
        )

        review_text = escape_html(
            item.get("review_text")
        )

        target = escape_html(
            item.get("target")
        )

        opinion = escape_html(
            item.get("opinion")
        )

        sentiment_value = normalize_sentiment(
            item.get("sentiment")
        )

        badge = get_sentiment_badge(
            sentiment_value
        )

        with st.expander(
            f"Review #{review_id} · "
            f"{sentiment_value.capitalize()}",
            expanded=index == 1,
        ):

            st.markdown(
                f"""
<div class="detail-card">
    <div class="detail-title">
        📝 Review #{review_id}
    </div>
    <div class="detail-label">
        Review Pelanggan
    </div>
    <div class="quote-box">
        "{review_text}"
    </div>
    <div class="detail-label">
        Target
    </div>
    <div class="detail-value">
        {target}
    </div>
    <div class="detail-label">
        Opinion
    </div>
    <div class="detail-value">
        "{opinion}"
    </div>
    <div class="detail-label">
        Sentiment
    </div>
    <div style="margin-top:5px;">
        {badge}
    </div>
</div>
""",
                unsafe_allow_html=True,
            )


def render_manual_evidence(
    active_aggregator,
    df_summary,
):

    st.subheader(
        "🔎 Detail Evidence Aspek"
    )

    st.caption(
        "Gunakan pilihan ini jika ingin melihat "
        "seluruh sentiment pada suatu aspek."
    )

    if df_summary.empty:

        st.info(
            "Belum ada evidence."
        )

        return

    all_categories = (
        df_summary
        .sort_values(
            "total_mentions",
            ascending=False,
        )["category"]
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

        if priority_names[0] in all_categories:

            default_index = (
                all_categories.index(
                    priority_names[0]
                )
            )

    selected_aspect = st.selectbox(
        "Pilih Aspek",
        all_categories,
        index=default_index,
        key="manual_aspect_selector",
    )

    evidence = (
        active_aggregator
        .get_evidence(
            selected_aspect
        )
    )

    if not evidence:
        return

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

    all_details = (
        active_aggregator
        .get_aspect_details(
            selected_aspect
        )
    )

    if not all_details:

        st.info(
            "Tidak ada detail penyebutan."
        )

        return

    st.markdown(
        "### 🧾 Detail Penyebutan"
    )

    for item in all_details:

        review_id = escape_html(
            item.get("review_id")
        )

        review_text = escape_html(
            item.get("review_text")
        )

        target = escape_html(
            item.get("target")
        )

        opinion = escape_html(
            item.get("opinion")
        )

        sentiment = normalize_sentiment(
            item.get("sentiment")
        )

        badge = get_sentiment_badge(
            sentiment
        )

        with st.expander(
            f"Review #{review_id} · "
            f"{sentiment.capitalize()}",
        ):

            st.markdown(
                f"""
<div class="detail-card">
    <div class="detail-label">
        Review Pelanggan
    </div>
    <div class="quote-box">
        "{review_text}"
    </div>
    <div class="detail-label">
        Target
    </div>
    <div class="detail-value">
        {target}
    </div>
    <div class="detail-label">
        Opinion
    </div>
    <div class="detail-value">
        "{opinion}"
    </div>
    <div class="detail-label">
        Sentiment
    </div>
    <div style="margin-top:5px;">
        {badge}
    </div>
</div>
""",
                unsafe_allow_html=True,
            )