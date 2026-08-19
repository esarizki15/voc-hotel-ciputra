import streamlit as st
from services.upload_service import process_uploaded_file


def render_upload():
    st.subheader("📂 Upload & Analisis Dataset")
    st.caption(
        "Upload CSV/XLSX berisi review pelanggan untuk dianalisis menggunakan Qwen3:8B."
    )

    uploaded_file = st.file_uploader(
        "Upload Dataset Review",
        type=["csv", "xlsx", "xls"],
    )

    if uploaded_file is None:
        return

    st.success(f"File siap diproses: **{uploaded_file.name}**")

    # Panggil langsung tanpa dibungkus st.button
    process_uploaded_file(uploaded_file)