import html


def escape_html(value) -> str:
    return html.escape(
        str(value if value is not None else "-")
    )


def normalize_sentiment(
    sentiment: str | None,
) -> str:

    value = str(
        sentiment or "netral"
    ).strip().lower()

    if value not in {
        "positif",
        "negatif",
        "netral",
    }:
        return "netral"

    return value


def get_sentiment_badge(
    sentiment: str | None,
) -> str:

    sentiment = normalize_sentiment(
        sentiment
    )

    if sentiment == "positif":

        return (
            '<span class="badge-positive">'
            "🟢 Positif"
            "</span>"
        )

    if sentiment == "negatif":

        return (
            '<span class="badge-negative">'
            "🔴 Negatif"
            "</span>"
        )

    return (
        '<span class="badge-neutral">'
        "🟡 Netral"
        "</span>"
    )


def get_sentiment_icon(
    sentiment: str | None,
) -> str:

    sentiment = normalize_sentiment(
        sentiment
    )

    if sentiment == "positif":
        return "🟢"

    if sentiment == "negatif":
        return "🔴"

    return "🟡"