voc-hotel-ciputra/
├── data/
│   ├── raw_terma.csv           # Dataset mentah IndoNLU TERMA
│   └── processed_reviews.json  # Hasil ekstraksi JSON dari Qwen3:8B
├── engine/
│   ├── __init__.py
│   ├── ollama_client.py        # Logic panggilan API Ollama + Prompting
│   └── aggregator.py           # Logic menghitung Priority Score & Statistik
├── evaluation/
│   └── evaluate_metrics.py     # Script penghiung Precision, Recall, F1-Score
├── app.py                      # Aplikasi Utama Streamlit Dashboard
├── requirements.txt            # Library (streamlit, ollama, pandas, scikit-learn)
└── README.md