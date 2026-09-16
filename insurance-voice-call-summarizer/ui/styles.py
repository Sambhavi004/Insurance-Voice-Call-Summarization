"""
Custom CSS styling for Insurance Voice Call Summarizer & Audit Platform.
"""

CUSTOM_CSS = """
<style>
/* App-wide styling */
.main {
    background-color: #f8fafc;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Header styling */
.header-container {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    padding: 24px 28px;
    border-radius: 12px;
    margin-bottom: 24px;
    color: #ffffff;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.12);
}

.header-title {
    font-size: 26px;
    font-weight: 700;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.header-subtitle {
    font-size: 14px;
    color: #94a3b8;
    margin-top: 6px;
}

/* KPI Card Styles */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    margin-bottom: 12px;
}

.kpi-title {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
    margin-top: 4px;
    color: #0f172a;
}

.kpi-badge-pass {
    display: inline-block;
    background-color: #dcfce7;
    color: #15803d;
    font-weight: 600;
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 9999px;
}

.kpi-badge-fail {
    display: inline-block;
    background-color: #fee2e2;
    color: #b91c1c;
    font-weight: 600;
    font-size: 12px;
    padding: 3px 10px;
    border-radius: 9999px;
}

/* Transcript Turns */
.turn-agent {
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 12px;
}

.turn-customer {
    background: #f8fafc;
    border-left: 4px solid #0284c7;
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 12px;
}

.turn-speaker {
    font-size: 13px;
    font-weight: 700;
    color: #334155;
    margin-bottom: 4px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.turn-text {
    font-size: 14px;
    color: #1e293b;
    line-height: 1.5;
}

/* Sentiment badges */
.badge-pos {
    background: #dcfce7;
    color: #166534;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
}

.badge-neg {
    background: #fee2e2;
    color: #991b1b;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
}

.badge-neu {
    background: #f1f5f9;
    color: #475569;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 12px;
}

/* Red flag alerts */
.red-flag-card-critical {
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-left: 6px solid #e11d48;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 14px;
}

.red-flag-card-high {
    background: #fff7ed;
    border: 1px solid #ffedd5;
    border-left: 6px solid #ea580c;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 14px;
}

.red-flag-card-medium {
    background: #fefce8;
    border: 1px solid #fef08a;
    border-left: 6px solid #ca8a04;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 14px;
}

.quote-box {
    font-style: italic;
    background: rgba(0, 0, 0, 0.04);
    border-left: 3px solid #94a3b8;
    padding: 6px 12px;
    margin: 8px 0;
    font-size: 13px;
}

/* Tab container */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    height: 44px;
    white-space: pre-wrap;
    background-color: #f1f5f9;
    border-radius: 6px 6px 0 0;
    padding: 10px 16px;
    font-weight: 600;
    color: #475569;
}

.stTabs [aria-selected="true"] {
    background-color: #ffffff !important;
    color: #0284c7 !important;
    border-top: 3px solid #0284c7 !important;
}
</style>
"""
