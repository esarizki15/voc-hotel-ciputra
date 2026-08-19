from pathlib import Path
import re
import pandas as pd
import streamlit as st

from engine.batch_processor import BatchProcessor
from engine.ollama_client import OllamaABSAClient

ALLOWED_REVIEW_COLUMNS = {"review", "review_text", "text", "ulasan", "content"}


def load_uploaded_dataframe(uploaded_file) -> pd.DataFrame:
    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    raise ValueError("Format file tidak didukung. Gunakan CSV atau Excel.")


def process_uploaded_file(uploaded_file):
    try:
        df = load_uploaded_dataframe(uploaded_file)
    except Exception as error:
        st.error(f"Gagal membaca file: {error}")
        return

    if df.empty:
        st.warning("File yang diunggah tidak memiliki data (kosong).")
        return

    st.write(f"**Total data:** {len(df):,} review")
    st.dataframe(df.head(5), use_container_width=True)

    # Deteksi kolom review
    possible_columns = [
        col for col in df.columns 
        if str(col).lower() in ALLOWED_REVIEW_COLUMNS
    ]

    if not possible_columns:
        st.error(
            "Tidak ditemukan kolom review. "
            "Gunakan nama seperti `review`, `review_text`, `text`, `ulasan`, atau `content`."
        )
        return

    review_column = possible_columns[0]
    st.info(f"Kolom review yang terdeteksi: **{review_column}**")

    # Clean missing values
    df[review_column] = df[review_column].fillna("").astype(str)

    if st.button("🚀 Mulai Analisis Dataset", type="primary", key="btn_start_batch_analysis"):
        client = OllamaABSAClient()

        if not client.is_available():
            st.error("❌ Ollama tidak dapat diakses. Pastikan service Ollama aktif.")
            return

        processor = BatchProcessor(ollama_client=client)
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(current: int, total: int):
            percentage = current / total if total > 0 else 0.0
            progress_bar.progress(percentage)
            status_text.write(f"Memproses {current:,} / {total:,} review...")

        try:
            with st.spinner("⏳ Sedang menganalisis dataset dengan Qwen3:8B..."):
                results = processor.process_dataframe(
                    df=df,
                    review_column=review_column,
                    progress_callback=update_progress,
                )

                # Buat nama file JSON unik berdasarkan nama file asli
                clean_stem = re.sub(r"[^\w\-]", "_", Path(uploaded_file.name).stem.lower())
                output_file_path = Path("data") / f"processed_{clean_stem}.json"

                processor.save_results(results, output_file_path)

                # Set dataset baru sebagai dataset aktif
                st.session_state["active_dataset"] = str(output_file_path)

            st.success(f"🎉 Analisis selesai! {len(results):,} review berhasil diproses.")
            st.info(f"💡 Dataset disimpan ke `{output_file_path.name}`. Silakan buka **Dashboard** untuk melihat visualisasi.")
            st.json(results[:3])

        except Exception as err:
            st.error(f"Terjadi kesalahan saat memproses data: {err}")