from collections import defaultdict
import streamlit as st

from utils.formatting import (
    escape_html,
    get_sentiment_badge,
    get_sentiment_icon,
    normalize_sentiment,
)


def group_by_review(details: list[dict]) -> dict[str | int, list[dict]]:
    """Mengelompokkan banyak aspek berdasarkan review_id yang sama."""
    grouped = defaultdict(list)
    for item in details:
        review_id = item.get("review_id", "N/A")
        grouped[review_id].append(item)
    return grouped


def render_aspect_details(
    active_aggregator,
    category: str,
    sentiment: str | None = None,
):
    details = active_aggregator.get_aspect_details(
        category_name=category,
        sentiment=sentiment,
    )

    if not details:
        st.info("Tidak ditemukan detail review untuk kombinasi aspek dan sentimen tersebut.")
        return

    if sentiment:
        sentiment = normalize_sentiment(sentiment)
        icon = get_sentiment_icon(sentiment)
        st.subheader(f"{icon} Detail {category} — {sentiment.capitalize()}")
    else:
        st.subheader(f"🔎 Detail Aspek — {category}")

    st.caption(f"Ditemukan {len(details)} penyebutan yang sesuai dengan filter.")

    positive_count = sum(1 for item in details if normalize_sentiment(item.get("sentiment")) == "positif")
    negative_count = sum(1 for item in details if normalize_sentiment(item.get("sentiment")) == "negatif")
    neutral_count = sum(1 for item in details if normalize_sentiment(item.get("sentiment")) == "netral")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("🟢 Positif", positive_count)
    with c2:
        st.metric("🔴 Negatif", negative_count)
    with c3:
        st.metric("🟡 Netral", neutral_count)

    st.markdown("### 🧾 Evidence Review")

    # Grouping berdasarkan review_id
    grouped_reviews = group_by_review(details)

    for index, (review_id, items) in enumerate(grouped_reviews.items(), start=1):
        first_item = items[0]
        review_text = escape_html(first_item.get("review_text", ""))

        with st.expander(
            f"Review #{review_id} · ({len(items)} Aspek Terdeteksi)",
            expanded=index == 1,
        ):
            st.markdown(
                f"""
                <div class="detail-card">
                    <div class="detail-title">📝 Review #{review_id}</div>
                    <div class="detail-label">Review Pelanggan</div>
                    <div class="quote-box">"{review_text}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("**Aspek Terdeteksi pada Review Ini:**")
            
            # Tampilkan seluruh aspek dari review ini di dalam 1 expander
            cols = st.columns([2, 2, 1])
            cols[0].caption("**Target**")
            cols[1].caption("**Opinion**")
            cols[2].caption("**Sentiment**")

            for sub_item in items:
                target = escape_html(sub_item.get("target", "-"))
                opinion = escape_html(sub_item.get("opinion", "-"))
                sent_val = normalize_sentiment(sub_item.get("sentiment"))
                badge = get_sentiment_badge(sent_val)

                c_target, c_opinion, c_badge = st.columns([2, 2, 1])
                c_target.write(target)
                c_opinion.write(f'"{opinion}"')
                c_badge.markdown(badge, unsafe_allow_html=True)


def render_manual_evidence(
    active_aggregator,
    df_summary,
):
    st.subheader("🔎 Detail Evidence Aspek")
    st.caption("Gunakan pilihan ini jika ingin melihat seluruh sentiment pada suatu aspek.")

    if df_summary.empty:
        st.info("Belum ada evidence.")
        return

    all_categories = (
        df_summary.sort_values("total_mentions", ascending=False)["category"].tolist()
    )

    priorities = active_aggregator.get_top_priorities(top_n=5)
    priority_names = [item["category"] for item in priorities]

    default_index = 0
    if priority_names and priority_names[0] in all_categories:
        default_index = all_categories.index(priority_names[0])

    selected_aspect = st.selectbox(
        "Pilih Aspek",
        all_categories,
        index=default_index,
        key="manual_aspect_selector",
    )

    evidence = active_aggregator.get_evidence(selected_aspect)
    if not evidence:
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Jumlah Penyebutan", evidence["total_mentions"])
    with c2:
        st.metric("Keluhan Negatif", evidence["negative_count"])
    with c3:
        st.metric("Proporsi Negatif", f"{evidence['negative_ratio']:.1f}%")

    all_details = active_aggregator.get_aspect_details(selected_aspect)
    if not all_details:
        st.info("Tidak ada detail penyebutan.")
        return

    st.markdown("### 🧾 Detail Penyebutan")

    # Grouping berdasarkan review_id
    grouped_reviews = group_by_review(all_details)

    for review_id, items in grouped_reviews.items():
        first_item = items[0]
        review_text = escape_html(first_item.get("review_text", ""))

        with st.expander(f"Review #{review_id} · ({len(items)} Aspek Terdeteksi)"):
            st.markdown(
                f"""
                <div class="detail-card">
                    <div class="detail-label">Review Pelanggan</div>
                    <div class="quote-box">"{review_text}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("**Aspek Terdeteksi pada Review Ini:**")
            
            for sub_item in items:
                target = escape_html(sub_item.get("target", "-"))
                opinion = escape_html(sub_item.get("opinion", "-"))
                sent_val = normalize_sentiment(sub_item.get("sentiment"))
                badge = get_sentiment_badge(sent_val)

                c_target, c_opinion, c_badge = st.columns([2, 2, 1])
                c_target.write(f"**Target:** {target}")
                c_opinion.write(f'**Opinion:** "{opinion}"')
                c_badge.markdown(badge, unsafe_allow_html=True)