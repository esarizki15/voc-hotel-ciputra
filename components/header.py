import streamlit as st


def render_styles():

    st.markdown(
        """
<style>

/* Menggunakan CSS Variables Streamlit agar adaptif otomatis (Light & Dark Mode) */

.header-container {
    background: var(--secondary-background-color);
    border-bottom: 2px solid #0ea5e9;
    border: 1px solid rgba(128, 128, 128, 0.15);
    padding: 22px 28px;
    border-radius: 12px;
    margin-bottom: 22px;
}

.header-title {
    color: var(--text-color);
    font-size: 28px;
    font-weight: 700;
    margin: 0;
}

.header-subtitle {
    color: var(--text-color);
    opacity: 0.7;
    font-size: 14px;
    margin-top: 6px;
}

.insight-card {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.15);
    border-left: 5px solid #0ea5e9;
    padding: 18px 22px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.insight-title {
    color: #0284c7;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
}

.insight-body {
    color: var(--text-color);
    font-size: 15px;
    line-height: 1.6;
}

.kpi-card {
    background: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    min-height: 120px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.kpi-label {
    font-size: 13px;
    color: var(--text-color);
    opacity: 0.8;
    font-weight: 600;
}

.kpi-sub {
    font-size: 11px;
    color: var(--text-color);
    opacity: 0.6;
    margin-top: 5px;
}

.quote-box {
    background-color: var(--background-color);
    border: 1px solid rgba(128, 128, 128, 0.15);
    border-left: 4px solid #ef4444;
    padding: 12px 18px;
    margin-top: 10px;
    border-radius: 0 8px 8px 0;
    font-style: italic;
    color: var(--text-color);
    font-size: 14px;
}

.detail-card {
    background-color: var(--secondary-background-color);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
}

.detail-title {
    font-size: 16px;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 8px;
}

.detail-label {
    font-size: 12px;
    color: var(--text-color);
    opacity: 0.6;
    font-weight: 600;
    text-transform: uppercase;
    margin-top: 8px;
}

.detail-value {
    font-size: 14px;
    color: var(--text-color);
    margin-top: 2px;
}

/* Badge Sentimen dengan Border Transparan agar Terbaca di Mode Terang maupun Gelap */
.badge-positive {
    display: inline-block;
    background-color: rgba(34, 197, 94, 0.15);
    color: var(--text-color);
    border: 1px solid #22c55e;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.badge-negative {
    display: inline-block;
    background-color: rgba(239, 68, 68, 0.15);
    color: var(--text-color);
    border: 1px solid #ef4444;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.badge-neutral {
    display: inline-block;
    background-color: rgba(234, 179, 8, 0.15);
    color: var(--text-color);
    border: 1px solid #eab308;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

</style>
""",
        unsafe_allow_html=True,
    )

def render_header():

    render_styles()

    st.markdown(
        """
<div class="header-container">
    <div class="header-title">
        🏨 AI-Powered Voice of Customer Intelligence
    </div>
    <div class="header-subtitle">
        Proof of Concept · Hospitality · Ciputra Group
    </div>
</div>
""",
        unsafe_allow_html=True,
    )