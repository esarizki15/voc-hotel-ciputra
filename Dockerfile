# Gunakan base image Python 3.10 yang ringan
FROM python:3.10-slim

# Set Working Directory di dalam container
WORKDIR /app

# Install dependencies sistem yang diperlukan
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt terlebih dahulu untuk memanfaatkan Docker Layer Caching
COPY requirements.txt .

# Install dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode aplikasi ke dalam container
COPY . .

# Expose port Streamlit
EXPOSE 8501

# Konfigurasi Environment Variables Streamlit & Ollama
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
# Secara default mengarah ke Ollama di host machine (bisa di-override saat docker run)
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434

# Command utama untuk menjalankan aplikasi Streamlit
CMD ["streamlit", "run", "app.py"]
