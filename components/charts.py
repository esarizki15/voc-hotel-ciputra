import streamlit as st
import plotly.graph_objects as go

from components.evidence import (
    render_aspect_details,
)


def render_sentiment_chart(
    active_aggregator,
    df_summary,
    top_aspects: int = 10,
):

    st.subheader(
        "📊 Sentimen Berdasarkan Aspek"
    )

    st.caption(
        f"Menampilkan {top_aspects} aspek dengan "
        "jumlah penyebutan tertinggi. "
        "Klik bagian grafik untuk melihat detail "
        "review yang membentuk angka tersebut."
    )

    if df_summary.empty:

        st.info(
            "Belum ada data aspek "
            "untuk divisualisasikan."
        )

        return

    chart_df = (
        df_summary
        .sort_values(
            "total_mentions",
            ascending=False,
        )
        .head(top_aspects)
        .sort_values(
            "total_mentions",
            ascending=True,
        )
        .reset_index(drop=True)
    )

    fig = go.Figure()

    sentiments = [
        (
            "positif",
            "Positif",
            "#22c55e",
            "🟢",
        ),
        (
            "netral",
            "Netral",
            "#eab308",
            "🟡",
        ),
        (
            "negatif",
            "Negatif",
            "#ef4444",
            "🔴",
        ),
    ]

    for sentiment, label, color, icon in sentiments:

        fig.add_trace(
            go.Bar(
                y=chart_df["category"],
                x=chart_df[
                    f"{sentiment}_count"
                ],
                name=label,
                orientation="h",
                marker_color=color,

                customdata=[
                    [
                        row["category"],
                        sentiment,
                    ]
                    for _, row
                    in chart_df.iterrows()
                ],

                hovertemplate=(
                    "<b>%{y}</b><br>"
                    f"Sentimen: {label}<br>"
                    "Jumlah: %{x}<br>"
                    "<extra>Klik untuk detail</extra>"
                ),
            )
        )

    fig.update_layout(
        barmode="stack",

        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",

        font=dict(
            color="#f8fafc"
        ),

        xaxis=dict(
            title="Jumlah Penyebutan",
            gridcolor="#334155",
        ),

        yaxis=dict(
            title="",
        ),

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),

        height=max(
            450,
            len(chart_df) * 55,
        ),

        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20,
        ),
    )

    chart_event = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun",
        key="sentiment_chart",
    )

    selected_category = None
    selected_sentiment = None

    try:

        if chart_event is not None:

            points = (
                chart_event
                .selection
                .points
            )

            if points:

                customdata = (
                    points[0]
                    .get("customdata")
                )

                if (
                    customdata
                    and len(customdata) >= 2
                ):

                    selected_category = (
                        str(customdata[0])
                    )

                    selected_sentiment = (
                        str(customdata[1])
                        .strip()
                        .lower()
                    )

    except Exception:

        selected_category = None
        selected_sentiment = None

    if (
        selected_category
        and selected_sentiment
    ):

        st.divider()

        render_aspect_details(
            active_aggregator,
            selected_category,
            selected_sentiment,
        )

    st.caption(
        f"Total kategori/aspek yang terdeteksi: "
        f"{len(df_summary)}. "
        f"Grafik dibatasi ke "
        f"{min(top_aspects, len(df_summary))} "
        "aspek teratas."
    )