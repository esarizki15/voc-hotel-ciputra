import streamlit as st

from utils.formatting import (
    escape_html,
    get_sentiment_badge,
    normalize_sentiment,
)


def render_live_analyzer(
    ollama_client,
):

    st.subheader(
        "🔍 Analisis Ulasan Pelanggan Secara Langsung"
    )

    st.caption(
        "Masukkan ulasan pelanggan berbahasa Indonesia. "
        "Qwen3:8B akan mengidentifikasi aspek, target, "
        "opini, dan sentimen."
    )

    default_review = (
        "Kamarnya sangat bersih dan staf resepsionis "
        "ramah, tetapi Wi-Fi di lantai 3 sangat lambat "
        "dan AC agak berisik."
    )

    user_review = st.text_area(
        "Masukkan Ulasan Pelanggan",
        value=default_review,
        height=130,
        placeholder=(
            "Contoh: Kamarnya bersih tetapi "
            "WiFi sangat lambat."
        ),
    )

    analyze_button = st.button(
        "🚀 Analisis dengan AI",
        type="primary",
    )

    if not analyze_button:
        return

    if not user_review.strip():

        st.error(
            "Silakan masukkan teks ulasan "
            "terlebih dahulu."
        )

        return

    if not ollama_client.is_available():

        st.error(
            "❌ Ollama tidak dapat diakses. "
            "Pastikan Ollama sedang berjalan."
        )

        st.code(
            "ollama serve",
            language="bash",
        )

        return

    with st.spinner(
        "🤖 Qwen3:8B sedang "
        "menganalisis ulasan..."
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

        return

    st.success(
        f"Analisis selesai. "
        f"{len(results)} aspek terdeteksi."
    )

    # ========================================================
    # SENTIMENT SUMMARY
    # ========================================================

    positive_count = sum(
        1
        for item in results
        if normalize_sentiment(
            item.get("sentiment")
        ) == "positif"
    )

    negative_count = sum(
        1
        for item in results
        if normalize_sentiment(
            item.get("sentiment")
        ) == "negatif"
    )

    neutral_count = sum(
        1
        for item in results
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

    st.divider()

    # ========================================================
    # ASPECTS
    # ========================================================

    st.subheader(
        "🎯 Aspek yang Terdeteksi"
    )

    columns = st.columns(2)

    for index, result in enumerate(
        results
    ):

        category = escape_html(
            result.get("category")
        )

        target = escape_html(
            result.get("target")
        )

        opinion = escape_html(
            result.get("opinion")
        )

        sentiment = normalize_sentiment(
            result.get("sentiment")
        )

        badge = get_sentiment_badge(
            sentiment
        )

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
                    f"**Sentimen:** {badge}",
                    unsafe_allow_html=True,
                )

    # ========================================================
    # INTERPRETATION
    # ========================================================

    st.divider()

    st.subheader(
        "💡 Interpretasi"
    )

    negative_aspects = [
        item
        for item in results
        if normalize_sentiment(
            item.get("sentiment")
        ) == "negatif"
    ]

    positive_aspects = [
        item
        for item in results
        if normalize_sentiment(
            item.get("sentiment")
        ) == "positif"
    ]

    if negative_aspects:

        names = ", ".join(
            str(
                item.get(
                    "category",
                    "-",
                )
            )
            for item in negative_aspects
        )

        st.warning(
            "Ulasan mengindikasikan "
            f"keluhan pada aspek: **{names}**."
        )

    if positive_aspects:

        names = ", ".join(
            str(
                item.get(
                    "category",
                    "-",
                )
            )
            for item in positive_aspects
        )

        st.success(
            "Ulasan memberikan penilaian "
            f"positif pada aspek: **{names}**."
        )

    if (
        not negative_aspects
        and not positive_aspects
    ):

        st.info(
            "Ulasan tidak menunjukkan "
            "sentimen positif maupun negatif "
            "yang kuat."
        )

    with st.expander(
        "🔧 Lihat Output JSON"
    ):

        st.json(
            {
                "aspects": results
            }
        )