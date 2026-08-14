# 🏨 AI-Powered Voice of Customer Intelligence

> Proof of Concept (PoC) untuk penerapan Artificial Intelligence dalam menganalisis Voice of Customer (VoC) pada industri perhotelan Ciputra Group.

## 📌 Overview

**AI-Powered Voice of Customer Intelligence** adalah Proof of Concept yang memanfaatkan **Large Language Model (LLM)** untuk melakukan analisis ulasan pelanggan secara otomatis menggunakan pendekatan **Aspect-Based Sentiment Analysis (ABSA)**.

Sistem mengidentifikasi:
- Aspek layanan/fasilitas yang dibicarakan
- Target spesifik dari aspek tersebut
- Opinion atau opini pelanggan
- Sentimen terhadap setiap aspek

Contoh:

> "Kamar saya ada kendala di AC tidak berfungsi optimal dan WiFi koneksi kurang stabil."

| Aspek | Target | Opini | Sentimen |
|---|---|---|---|
| AC | AC kamar | tidak berfungsi optimal | 🔴 Negatif |
| WiFi | wifi koneksi | kurang stabil | 🔴 Negatif |

## 🎯 Tujuan PoC

1. Mengolah review pelanggan dalam jumlah besar.
2. Mengidentifikasi aspek yang paling sering dibicarakan.
3. Mengukur sentimen pada setiap aspek.
4. Menentukan area yang perlu mendapatkan perhatian.
5. Mengidentifikasi keunggulan layanan.
6. Menampilkan evidence berupa review pelanggan.
7. Menyediakan analisis review secara real-time.

Tujuan akhirnya adalah membangun konsep **Voice of Customer Intelligence** yang dapat digunakan sebagai dasar pengambilan keputusan dan improvement operasional hotel.

## 🧠 Pendekatan AI

```text
Review
   ↓
Aspect Extraction
   ↓
Target Extraction
   ↓
Opinion Extraction
   ↓
Sentiment Classification
   ↓
Business Aggregation
   ↓
Executive Insight
```

## 🤖 Model

PoC menggunakan **Qwen3:8B** yang dijalankan secara lokal menggunakan **Ollama**.

Keuntungan pendekatan ini:
- Tidak membutuhkan API cloud.
- Data review tidak perlu dikirim ke layanan eksternal.
- Dapat dijalankan secara lokal.
- Cocok untuk eksperimen dan pengembangan awal.
- Model dapat diganti di kemudian hari tanpa mengubah keseluruhan arsitektur.

## 📚 Dataset

### IndoNLU TERMA

Dataset yang digunakan pada tahap PoC adalah **IndoNLU TERMA**.

Dataset digunakan sebagai **data awal untuk menguji pipeline ABSA**, karena data review hotel Ciputra aktual belum tersedia pada tahap pengembangan PoC.

```text
TERMA Dataset
      ↓
Rekonstruksi Kalimat
      ↓
Qwen3:8B
      ↓
Aspect-Based Sentiment Analysis
      ↓
processed_reviews.json
      ↓
Aggregator
      ↓
Streamlit Dashboard
```

> ⚠️ **Dataset TERMA bukan merupakan data pelanggan Ciputra.**

Penggunaan TERMA pada tahap ini bertujuan untuk menguji pipeline, kemampuan model, dashboard, dan demonstrasi konsep.

Ketika data review hotel Ciputra sudah tersedia, dataset dapat diganti tanpa perlu mengubah konsep utama sistem.

## 🏗️ Arsitektur Sistem

```text
                    ┌─────────────────────┐
                    │   Review Dataset    │
                    │  TERMA / Hotel      │
                    │      Ciputra        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Batch Processor     │
                    │ Rekonstruksi Review │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Qwen3:8B        │
                    │      Ollama         │
                    │        ABSA         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ processed_reviews   │
                    │       .json         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    Aggregator       │
                    │ Aspect Aggregation  │
                    │ Sentiment Analysis  │
                    │ Priority Scoring    │
                    │ Evidence Extraction│
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Streamlit       │
                    │     Dashboard       │
                    └─────────────────────┘
```

## 📁 Project Structure

```text
voc-hotel-ciputra/
│
├── data/
│   ├── train_preprocess.txt
│   └── processed_reviews.json
│
├── engine/
│   ├── __init__.py
│   ├── ollama_client.py
│   ├── batch_processor.py
│   └── aggregator.py
│
├── app.py
├── requirements.txt
└── README.md
```

## ⚙️ Requirements

- Python 3.10+
- Ollama
- Qwen3:8B
- pip
- virtual environment

Library Python utama:

```text
streamlit
pandas
plotly
requests
```

## 🚀 Installation

### 1. Buka project

```bash
cd voc-hotel-ciputra
```

### 2. Buat virtual environment

```bash
python -m venv venv
```

macOS/Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependency

```bash
pip install -r requirements.txt
```

## 🤖 Setup Ollama

Download model:

```bash
ollama pull qwen3:8b
```

Jalankan Ollama:

```bash
ollama serve
```

Cek model:

```bash
ollama list
```

## 🧪 Menjalankan Batch Processing

Dataset TERMA berada di:

```text
data/train_preprocess.txt
```

15 review:

```bash
python -m engine.batch_processor --limit 15
```

50 review:

```bash
python -m engine.batch_processor --limit 50
```

Seluruh dataset:

```bash
python -m engine.batch_processor --limit 999999
```

Hasil analisis:

```text
data/processed_reviews.json
```

Contoh output:

```json
{
  "review_id": 1,
  "review_text": "kamar saya ada kendala di ac tidak berfungsi optimal . dan juga wifi koneksi kurang stabil .",
  "aspects": [
    {
      "category": "AC",
      "target": "AC kamar",
      "opinion": "tidak berfungsi optimal",
      "sentiment": "negatif"
    },
    {
      "category": "WiFi",
      "target": "wifi koneksi",
      "opinion": "kurang stabil",
      "sentiment": "negatif"
    }
  ],
  "status": "success",
  "error": null
}
```

## 🖥️ Menjalankan Dashboard

Setelah batch processing selesai:

```bash
streamlit run app.py
```

## 📊 Dashboard

Dashboard memiliki dua bagian utama.

### 1. Dashboard Inteligensi Pelanggan

Menampilkan:
- Total Ulasan
- Persentase aspek positif
- Prioritas Perbaikan #1
- Keunggulan Utama
- Prioritas perbaikan
- Keunggulan layanan
- Sentimen berdasarkan aspek
- Evidence review pelanggan
- Rekapitulasi aspek

### 2. Live Review Analyzer

Memungkinkan pengguna memasukkan review berbahasa Indonesia dan melihat aspek serta sentimen yang terdeteksi Qwen3:8B secara real-time.

Contoh:

```text
Kamarnya sangat bersih dan staf resepsionis ramah,
tetapi Wi-Fi di lantai 3 sangat lambat dan AC agak berisik.
```

## 📈 Priority Score

Priority Score saat ini menggunakan formula sederhana:

```text
Priority Score
=
Total Mentions × Negative Ratio × 10
```

Contoh:

```text
WiFi

Total Mentions = 20
Negative       = 12

Negative Ratio = 12 / 20
               = 60%

Priority Score = 20 × 0.60 × 10
               = 120
```

Semakin tinggi skor, semakin layak aspek tersebut diprioritaskan untuk evaluasi.

> Priority Score merupakan **relative prioritization score**, bukan ukuran absolut tingkat kepuasan pelanggan dan bukan bukti hubungan kausal bahwa memperbaiki aspek tertentu pasti meningkatkan kepuasan.

## 🏨 Roadmap untuk Ciputra

PoC dirancang agar dataset dapat diganti dari:

```text
IndoNLU TERMA
```

menjadi:

```text
Review Hotel Ciputra
```

Target pipeline:

```text
Review Hotel Ciputra
        │
        ├── OTA
        ├── Google Reviews
        ├── Internal Guest Feedback
        ├── Survey
        └── CRM
              │
              ▼
       Review Collector
              │
              ▼
        Data Processing
              │
              ▼
          Qwen / LLM
              │
              ▼
             ABSA
              │
              ▼
       Central Database
              │
              ▼
      VoC Intelligence
              │
       ┌──────┴──────┐
       ▼             ▼
   Dashboard      Reporting
```

## 🔮 Pengembangan Berikutnya

### 1. Multi-Hotel Intelligence

Membandingkan performa beberapa hotel berdasarkan aspek dan sentimen.

### 2. Trend Analysis

Melihat perubahan keluhan dari waktu ke waktu.

```text
Jan → Feb → Mar → Apr → ...
```

### 3. Cross-Hotel Benchmarking

Membandingkan aspek antar hotel.

### 4. Automated Alert

Memberikan alert ketika terjadi peningkatan keluhan tertentu.

### 5. Executive Recommendation

Menambahkan rekomendasi berbasis insight sebagai **decision support**, bukan keputusan otomatis.

## 🔐 Data Privacy

Pada PoC:
- Model berjalan secara lokal menggunakan Ollama.
- Dataset tidak dikirim ke API LLM eksternal.
- Data pelanggan aktual belum digunakan.

Jika dikembangkan ke production, perlu dipertimbangkan:
- Anonimisasi data pelanggan
- Data governance
- Access control
- Audit log
- Retention policy
- Security review
- Compliance terhadap kebijakan internal perusahaan

## ⚠️ Current Limitations

### Dataset

Data yang digunakan masih **IndoNLU TERMA** dan belum merupakan review aktual hotel Ciputra.

### Model

Qwen3:8B digunakan melalui prompting dan belum melalui fine-tuning khusus domain perhotelan Ciputra.

### Evaluation

PoC belum memiliki evaluasi benchmark khusus untuk:
- Aspect Extraction Accuracy
- Sentiment Accuracy
- Precision
- Recall
- F1-Score

Evaluasi dapat menjadi tahap berikutnya setelah tersedia dataset berlabel yang representatif.

### Priority Score

Priority Score masih berupa formula heuristik sederhana dan perlu divalidasi bersama stakeholder bisnis sebelum digunakan sebagai KPI operasional.

## 🎯 Business Value

Jika dikembangkan menggunakan data review aktual hotel Ciputra:

```text
                 CUSTOMER REVIEWS
                       │
                       ▼
                  AI ANALYSIS
                       │
                       ▼
              CUSTOMER VOICE DATA
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          Problems  Strengths  Trends
             │         │         │
             └─────────┼─────────┘
                       ▼
                BUSINESS INSIGHT
                       │
                       ▼
               IMPROVEMENT ACTION
```

Review pelanggan tidak hanya menjadi kumpulan komentar, tetapi dapat diubah menjadi **structured intelligence untuk mendukung keputusan bisnis dan improvement layanan perhotelan**.

## 👨‍💻 Technology Stack

| Komponen | Teknologi |
|---|---|
| Language | Python |
| LLM | Qwen3:8B |
| LLM Runtime | Ollama |
| NLP Approach | Aspect-Based Sentiment Analysis |
| Dataset PoC | IndoNLU TERMA |
| Dashboard | Streamlit |
| Data Processing | Pandas |
| Visualization | Plotly |
| Output | JSON |

## 📌 Project Status

**Status: Proof of Concept**

Current:

```text
✅ TERMA dataset
✅ Review reconstruction
✅ Qwen3:8B integration
✅ Aspect extraction
✅ Target extraction
✅ Opinion extraction
✅ Sentiment classification
✅ Batch processing
✅ Priority scoring
✅ Evidence extraction
✅ Executive dashboard
✅ Live review analyzer
```

Next:

```text
⬜ Dataset review hotel Ciputra
⬜ Dataset labeling / validation
⬜ Model evaluation
⬜ Multi-hotel analysis
⬜ Historical trend analysis
⬜ Automated alert
⬜ Production architecture
```

## 💡 Key Message

> **AI-Powered Voice of Customer Intelligence mengubah review pelanggan menjadi insight terstruktur mengenai apa yang disukai, apa yang dikeluhkan, dan area mana yang perlu diprioritaskan untuk improvement layanan perhotelan.**

PoC saat ini menggunakan **IndoNLU TERMA sebagai data pengujian**, sedangkan implementasi sebenarnya ditujukan untuk dapat menggunakan **review aktual hotel Ciputra** ketika data tersedia.
