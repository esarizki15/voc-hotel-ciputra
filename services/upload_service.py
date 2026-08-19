import pandas as pd
import streamlit as st

from config.settings import (
    PROCESSED_DATA_PATH,
)
from engine.batch_processor import (
    BatchProcessor,
)
from engine.ollama_client import (
    OllamaABSAClient,
)


def load_uploaded_dataframe(
    uploaded_file,
):

    filename = (
        uploaded_file.name
        .lower()
    )

    if filename.endswith(".csv"):

        return pd.read_csv(
            uploaded_file
        )

    if filename.endswith(".xlsx"):

        return pd.read_excel(
            uploaded_file
        )

    raise ValueError(
        "Format file tidak didukung."
    )


def process_uploaded_file(
    uploaded_file,
):

    try:

        df = load_uploaded_dataframe(
            uploaded_file
        )

    except Exception as error:

        st.error(
            f"Gagal membaca file: {error}"
        )

        return

    st.write(
        f"**Total data:** {len(df):,} review"
    )

    st.dataframe(
        df.head(10),
        use_container_width=True,
    )

    # Sesuaikan nama kolom dengan dataset
    possible_columns = [
        column
        for column in df.columns
        if str(column).lower()
        in {
            "review",
            "review_text",
            "text",
            "ulasan",
            "content",
        }
    ]

    if not possible_columns:

        st.error(
            "Tidak ditemukan kolom review. "
            "Gunakan nama seperti "
            "`review`, `review_text`, `text`, "
            "`ulasan`, atau `content`."
        )

        return

    review_column = (
        possible_columns[0]
    )

    st.info(
        f"Kolom review yang digunakan: "
        f"**{review_column}**"
    )

    if not st.button(
        "Konfirmasi & Proses",
        type="primary",
        key="confirm_batch_processing",
    ):
        return

    client = OllamaABSAClient()

    if not client.is_available():

        st.error(
            "Ollama tidak dapat diakses."
        )

        return

    processor = BatchProcessor(
        ollama_client=client
    )

    progress_bar = st.progress(
        0
    )

    status_text = st.empty()

    results = processor.process_dataframe(
        df=df,
        review_column=review_column,
        progress_callback=lambda current, total: (
            progress_bar.progress(
                current / total
            ),
            status_text.write(
                f"Memproses {current:,} "
                f"/ {total:,} review..."
            ),
        ),
    )

    processor.save_results(
        results,
        PROCESSED_DATA_PATH,
    )

    st.success(
        f"🎉 Analisis selesai. "
        f"{len(results):,} review diproses."
    )

    st.info(
        "Dataset hasil analisis telah disimpan "
        "dan siap digunakan dashboard."
    )

    st.json(
        results[:3]
    )

    st.warning(
        "Refresh halaman/dashboard untuk "
        "memuat dataset terbaru."
    )