import html
import streamlit as st

from utils.formatting import (
    get_sentiment_badge,
    normalize_sentiment,
)


def render_live_analyzer(ollama_client):
    st.subheader("🔍 Analisis Ulasan Pelanggan Secara Langsung")
    st.caption(
        "Masukkan ulasan pelanggan berbahasa Indonesia. Qwen3:8B akan mengidentifikasi aspek, target, opini, dan sentimen."
    )

    default_review = (
        "Kamarnya sangat bersih dan staf resepsionis ramah, tetapi Wi-Fi di lantai 3 sangat lambat dan AC agak berisik."
    )

    user_review = st.text_area(
        "Masukkan Ulasan Pelanggan",
        value=default_review,
        height=130,
        placeholder="Contoh: Kamarnya bersih tetapi WiFi sangat lambat.",
    )

    analyze_button = st.button(
        "🚀 Analisis dengan AI",
        type="primary",
        use_container_width=False,
    )

    # Menggunakan alur bersyarat tunggal (seperti kodingan lama Anda)
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
                st.caption(
                    "Pastikan model Qwen3:8B tersedia di Ollama dan teks mengandung aspek layanan atau fasilitas."
                )
            else:
                st.success(f"Analisis selesai. {len(results)} aspek terdeteksi.")

                # ========================================================
                # SENTIMENT SUMMARY
                # ========================================================
                positive_count = sum(
                    1 for item in results if normalize_sentiment(item.get("sentiment", "")) == "positif"
                )
                negative_count = sum(
                    1 for item in results if normalize_sentiment(item.get("sentiment", "")) == "negatif"
                )
                neutral_count = sum(
                    1 for item in results if normalize_sentiment(item.get("sentiment", "")) == "netral"
                )

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("🟢 Positif", positive_count)
                with c2:
                    st.metric("🔴 Negatif", negative_count)
                with c3:
                    st.metric("🟡 Netral", neutral_count)

                st.divider()

                # ========================================================
                # ASPECTS
                # ========================================================
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

                # ========================================================
                # INTERPRETATION
                # ========================================================
                st.subheader("💡 Interpretasi")
                negative_aspects = [
                    item for item in results if normalize_sentiment(item.get("sentiment", "")) == "negatif"
                ]
                positive_aspects = [
                    item for item in results if normalize_sentiment(item.get("sentiment", "")) == "positif"
                ]

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