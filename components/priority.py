import streamlit as st


def render_priorities(
    active_aggregator,
):

    col_left, col_right = st.columns(2)

    # ========================================================
    # PRIORITY
    # ========================================================

    with col_left:

        st.subheader(
            "🔥 Prioritas Perbaikan"
        )

        st.caption(
            "Aspek dengan volume penyebutan "
            "dan proporsi sentimen negatif yang tinggi."
        )

        priorities = (
            active_aggregator
            .get_top_priorities(top_n=5)
        )

        if not priorities:

            st.success(
                "Belum terdapat aspek negatif "
                "yang cukup untuk membentuk prioritas."
            )

        else:

            for rank, item in enumerate(
                priorities,
                start=1,
            ):

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### #{rank} "
                        f"{item['category']}"
                    )

                    st.caption(
                        f"{item['total_mentions']} "
                        f"penyebutan · "
                        f"{item['negative_count']} "
                        f"keluhan negatif"
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

        st.subheader(
            "🟢 Keunggulan Layanan"
        )

        st.caption(
            "Aspek dengan proporsi sentimen positif "
            "tinggi dan jumlah penyebutan yang memadai."
        )

        strengths = (
            active_aggregator
            .get_top_strengths(top_n=5)
        )

        if not strengths:

            st.info(
                "Belum terdapat cukup data "
                "untuk menentukan keunggulan layanan."
            )

        else:

            for rank, item in enumerate(
                strengths,
                start=1,
            ):

                with st.container(
                    border=True
                ):

                    st.markdown(
                        f"### #{rank} "
                        f"{item['category']}"
                    )

                    st.caption(
                        f"{item['total_mentions']} "
                        f"penyebutan · "
                        f"{item['positive_count']} "
                        f"sentimen positif"
                    )

                    st.metric(
                        "Proporsi Positif",
                        f"{item['positive_ratio']:.1f}%",
                    )