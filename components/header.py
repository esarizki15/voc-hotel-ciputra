import streamlit as st


def render_styles():

    st.markdown(
        """
<style>

.header-container {
    background: linear-gradient(
        135deg,
        #1e293b 0%,
        #0f172a 100%
    );
    border-bottom: 2px solid #38bdf8;
    padding: 22px 28px;
    border-radius: 12px;
    margin-bottom: 22px;
}

.header-title {
    color: #f8fafc;
    font-size: 28px;
    font-weight: 700;
    margin: 0;
}

.header-subtitle {
    color: #94a3b8;
    font-size: 14px;
    margin-top: 6px;
}

.insight-card {
    background-color: #1e293b;
    border-left: 5px solid #0ea5e9;
    padding: 18px 22px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.insight-title {
    color: #38bdf8;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 8px;
}

.insight-body {
    color: #e2e8f0;
    font-size: 15px;
    line-height: 1.6;
}

.kpi-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    min-height: 120px;
}

.kpi-value {
    font-size: 30px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 5px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.kpi-label {
    font-size: 13px;
    color: #94a3b8;
    font-weight: 600;
}

.kpi-sub {
    font-size: 11px;
    color: #64748b;
    margin-top: 5px;
}

.quote-box {
    background-color: #0f172a;
    border-left: 4px solid #ef4444;
    padding: 12px 18px;
    margin-top: 10px;
    border-radius: 0 8px 8px 0;
    font-style: italic;
    color: #cbd5e1;
    font-size: 14px;
}

.detail-card {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 12px;
}

.detail-title {
    font-size: 16px;
    font-weight: 700;
    color: #f8fafc;
    margin-bottom: 8px;
}

.detail-label {
    font-size: 12px;
    color: #64748b;
    font-weight: 600;
    text-transform: uppercase;
    margin-top: 8px;
}

.detail-value {
    font-size: 14px;
    color: #e2e8f0;
    margin-top: 2px;
}

.badge-positive {
    display: inline-block;
    background-color: rgba(34, 197, 94, 0.15);
    color: #86efac;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.badge-negative {
    display: inline-block;
    background-color: rgba(239, 68, 68, 0.15);
    color: #fca5a5;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.badge-neutral {
    display: inline-block;
    background-color: rgba(234, 179, 8, 0.15);
    color: #fde047;
    padding: 4px 10px;
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