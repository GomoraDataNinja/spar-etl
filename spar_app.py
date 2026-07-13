import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import hashlib
import re
import smtplib
import time
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================
# FORCE LIGHT MODE - PREVENT DARK THEME ISSUES
# ============================================
try:
    st._config.set_option('theme.base', 'light')
except:
    pass

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="SPAR Dynamics 365",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CSS STYLING
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .stApp {
        background: #f5f7fa;
    }
    
    .block-container {
        padding: 1.5rem 2rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }
    
    .login-centered {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f4e 50%, #2d1b69 100%);
    }
    
    .login-card-tight {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 2.5rem 2rem 2rem 2rem;
        max-width: 400px;
        width: 100%;
        box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        border: 1px solid rgba(255,255,255,0.2);
        text-align: center;
    }
    
    .app-name-tight {
        font-size: 2rem;
        font-weight: 700;
        color: #002B5C;
        margin-bottom: 0.25rem;
    }
    
    .app-name-tight .highlight {
        color: #E3000F;
    }
    
    .signin-text-tight {
        font-size: 0.85rem;
        color: #6B7280;
        margin-bottom: 0.25rem;
    }
    
    .version-info-tight {
        font-size: 0.65rem;
        color: #9aa0a6;
        margin-bottom: 1.5rem;
    }
    
    .spar-logo-small {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    .spar-logo-small .logo-icon {
        background: #E3000F;
        color: white;
        font-weight: 800;
        font-size: 1.5rem;
        padding: 0.1rem 0.8rem;
        border-radius: 6px;
        letter-spacing: 1.5px;
    }
    
    .spar-logo-small .logo-text {
        font-weight: 700;
        color: #002B5C;
        font-size: 1.2rem;
    }
    
    label, .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #202124 !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #dadce0 !important;
        padding: 0.6rem 0.75rem !important;
        font-size: 0.85rem !important;
        background: white !important;
        color: #202124 !important;
    }
    
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 1px solid #dadce0 !important;
        background: white !important;
    }
    
    .stSelectbox > div > div > div {
        color: #202124 !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        background: white !important;
    }
    
    div[data-baseweb="select"] li {
        color: #202124 !important;
        font-weight: 500 !important;
        background: white !important;
    }
    
    div[data-baseweb="select"] li:hover {
        background: #e8f0fe !important;
        color: #0052A5 !important;
    }
    
    div[data-testid="stMetric"] label {
        color: #5f6368 !important;
        font-size: 0.7rem !important;
    }
    
    div[data-testid="stMetric"] div {
        color: #002B5C !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }
    
    .stButton > button {
        background: #002B5C !important;
        color: white !important;
        border: none;
        border-radius: 24px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        font-size: 0.8rem;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #004080 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,43,92,0.3);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    .stButton > button[kind="secondary"] {
        background: #e9ecef !important;
        color: #495057 !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #dde1e6 !important;
    }
    
    .modern-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid #e8eaed;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    
    .card-header {
        font-size: 0.9rem;
        font-weight: 600;
        color: #202124 !important;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #e8eaed;
        padding-bottom: 0.5rem;
    }
    
    .modern-header {
        background: linear-gradient(135deg, #002B5C 0%, #004080 50%, #0052A5 100%);
        padding: 1.25rem 1.5rem;
        border-radius: 16px;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    .modern-header h1 {
        font-size: 1.5rem;
        font-weight: 600;
        color: white !important;
        margin-bottom: 0.25rem;
    }
    
    .modern-header p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 0.75rem;
    }
    
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.4rem 1rem;
        background: white;
        border-radius: 40px;
        margin-bottom: 1rem;
        border: 1px solid #e8eaed;
    }
    
    .logo-text {
        font-size: 0.9rem;
        font-weight: 600;
        color: #002B5C;
    }
    
    .role-badge {
        background: #002B5C;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        color: white;
        font-size: 0.6rem;
        font-weight: 500;
    }
    
    .user-name-badge {
        background: #f0f2f5;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        color: #5f6368;
        font-size: 0.65rem;
        font-weight: 500;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.25rem;
        background-color: white;
        padding: 0.25rem;
        border-radius: 40px;
        margin-bottom: 1rem;
        border: 1px solid #e8eaed;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 32px;
        padding: 0.35rem 1rem;
        font-size: 0.75rem;
        font-weight: 500;
        color: #5f6368;
    }
    
    .stTabs [aria-selected="true"] {
        background: #002B5C;
        color: white;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .status-badge {
        padding: 0.15rem 0.6rem;
        border-radius: 12px;
        font-size: 0.65rem;
        font-weight: 600;
        display: inline-block;
    }
    .status-badge.draft { background: #e9ecef; color: #495057; }
    .status-badge.confirmed { background: #cce5ff; color: #004085; }
    .status-badge.shipped { background: #d1ecf1; color: #0c5460; }
    .status-badge.delivered { background: #d4edda; color: #155724; }
    .status-badge.cancelled { background: #f8d7da; color: #721c24; }
    .status-badge.open { background: #fff3cd; color: #856404; }
    .status-badge.paid { background: #d4edda; color: #155724; }
    .status-badge.overdue { background: #f8d7da; color: #721c24; }
    .status-badge.received { background: #d4edda; color: #155724; }
    .status-badge.partial { background: #fff3cd; color: #856404; }
    .status-badge.synced { background: #d4edda; color: #155724; }
    .status-badge.processing { background: #cce5ff; color: #004085; }
    .status-badge.in-stock { background: #d4edda; color: #155724; }
    .status-badge.low-stock { background: #fff3cd; color: #856404; }
    .status-badge.out-of-stock { background: #f8d7da; color: #721c24; }
    .status-badge.approved { background: #d4edda; color: #155724; }
    .status-badge.rejected { background: #f8d7da; color: #721c24; }
    .status-badge.pending { background: #fff3cd; color: #856404; }
    
    ::placeholder {
        color: #9aa0a6 !important;
        opacity: 1 !important;
    }
    
    .stAlert div, .stAlert p {
        color: #202124 !important;
    }
    
    .stSelectbox svg {
        fill: #5f6368 !important;
    }
    
    .stMarkdown, .stMarkdown p {
        color: #202124 !important;
    }
    
    input[type="text"], input[type="email"], input[type="password"] {
        color: #202124 !important;
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #e8eaed;
        transition: all 0.2s;
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }
    
    .metric-card .icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #002B5C;
        margin-bottom: 0.2rem;
    }
    
    .metric-card .label {
        font-size: 0.7rem;
        color: #6B7280;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card .trend {
        font-size: 0.7rem;
        margin-top: 0.3rem;
        font-weight: 500;
    }
    
    .metric-card .trend.up { color: #28a745; }
    .metric-card .trend.down { color: #dc3545; }
    
    .metric-card .indicator {
        position: absolute;
        top: 0;
        right: 0;
        width: 4px;
        height: 100%;
    }
    .metric-card .indicator.blue { background: #0052A5; }
    .metric-card .indicator.green { background: #28a745; }
    .metric-card .indicator.yellow { background: #ffc107; }
    .metric-card .indicator.red { background: #dc3545; }
    .metric-card .indicator.purple { background: #6f42c1; }
    
    .quick-actions {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    
    .quick-action {
        background: white;
        border: 1px solid #e8eaed;
        border-radius: 10px;
        padding: 1rem 0.5rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s;
        text-decoration: none;
        color: #202124;
    }
    
    .quick-action:hover {
        background: #002B5C;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,43,92,0.2);
    }
    
    .quick-action i {
        font-size: 1.5rem;
        display: block;
        margin-bottom: 0.3rem;
    }
    
    .quick-action .label {
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .quick-action:hover .label { color: white; }
    
    .content-grid {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 1.5rem;
        margin-bottom: 1.5rem;
    }
    
    .card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e8eaed;
        overflow: hidden;
    }
    
    .card .card-header {
        padding: 1rem 1.25rem;
        border-bottom: 1px solid #e8eaed;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
    }
    
    .card .card-header h3 {
        font-size: 0.9rem;
        font-weight: 600;
        color: #202124;
    }
    
    .card .card-header .link {
        font-size: 0.75rem;
        color: #0052A5;
        text-decoration: none;
        font-weight: 500;
        cursor: pointer;
    }
    
    .card .card-body {
        padding: 1rem 1.25rem;
        overflow-x: auto;
    }
    
    .activity-list {
        list-style: none;
    }
    .activity-list li {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.6rem 0;
        border-bottom: 1px solid #f0f2f5;
    }
    .activity-list li:last-child { border-bottom: none; }
    .activity-list .info .title { font-weight: 500; font-size: 0.85rem; }
    .activity-list .info .meta { font-size: 0.7rem; color: #6B7280; }
    .activity-list .amount { font-weight: 600; font-size: 0.85rem; }
    
    .filter-bar {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        margin-bottom: 1rem;
    }
    .filter-bar input, .filter-bar select {
        padding: 0.4rem 0.75rem;
        border: 1px solid #dadce0;
        border-radius: 8px;
        font-size: 0.85rem;
        font-family: 'Inter', sans-serif;
        background: white;
        color: #202124;
    }
    
    .table-container {
        overflow-x: auto;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    table th {
        text-align: left;
        padding: 0.5rem;
        border-bottom: 2px solid #e8eaed;
        color: #6B7280;
        font-weight: 600;
        font-size: 0.7rem;
        text-transform: uppercase;
    }
    table td {
        padding: 0.5rem;
        border-bottom: 1px solid #f0f2f5;
    }
    table tr:hover {
        background: #f8f9fa;
    }
    
    .btn-approve {
        background: #28a745;
        color: white;
        border: none;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.7rem;
        transition: all 0.2s;
        margin-right: 0.2rem;
    }
    .btn-approve:hover {
        background: #218838;
    }
    
    .btn-reject {
        background: #dc3545;
        color: white;
        border: none;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.7rem;
        transition: all 0.2s;
    }
    .btn-reject:hover {
        background: #c82333;
    }
    
    .btn-delete {
        background: #dc3545;
        color: white;
        border: none;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.7rem;
        transition: all 0.2s;
    }
    .btn-delete:hover {
        background: #c82333;
    }
    
    .btn-receipt {
        background: #0052A5;
        color: white;
        border: none;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.65rem;
        transition: all 0.2s;
    }
    .btn-receipt:hover {
        background: #004080;
    }
    
    .item-row {
        display: grid;
        grid-template-columns: 2fr 0.8fr 0.8fr 0.5fr;
        gap: 0.5rem;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .item-row input, .item-row select {
        padding: 0.4rem 0.5rem;
        border: 1px solid #dadce0;
        border-radius: 6px;
        font-size: 0.8rem;
        font-family: 'Inter', sans-serif;
        background: white;
        color: #202124;
    }
    .item-row .remove-btn {
        background: #dc3545;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.4rem;
        cursor: pointer;
        font-size: 0.8rem;
    }
    .item-row .remove-btn:hover {
        background: #c82333;
    }
    .add-item-btn {
        background: #e9ecef;
        border: none;
        padding: 0.3rem 1rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.75rem;
        color: #495057;
        transition: all 0.2s;
    }
    .add-item-btn:hover {
        background: #dee2e6;
    }
    
    .order-summary {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.75rem;
        margin: 1rem 0;
    }
    .order-summary .row {
        display: flex;
        justify-content: space-between;
        padding: 0.2rem 0;
    }
    .order-summary .total {
        border-top: 2px solid #e8eaed;
        padding-top: 0.5rem;
        margin-top: 0.3rem;
        font-size: 1.1rem;
        font-weight: 700;
        color: #002B5C;
    }
    
    .receipt-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 15px;
        background: white;
        border-radius: 8px;
    }
    .receipt-container .receipt-header {
        text-align: center;
        border-bottom: 2px solid #e8eaed;
        padding-bottom: 10px;
        margin-bottom: 10px;
    }
    .receipt-container .receipt-header h2 {
        color: #002B5C;
        font-size: 1.2rem;
    }
    .receipt-container .receipt-header p {
        font-size: 0.75rem;
        color: #6B7280;
        margin: 2px 0;
    }
    .receipt-container .receipt-info {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.2rem;
        font-size: 0.75rem;
        margin-bottom: 8px;
    }
    .receipt-container .receipt-info .label {
        font-weight: 600;
        color: #6B7280;
    }
    .receipt-container .receipt-table {
        width: 100%;
        font-size: 0.75rem;
        border-collapse: collapse;
        margin: 8px 0;
    }
    .receipt-container .receipt-table th {
        text-align: left;
        padding: 0.3rem;
        border-bottom: 1px solid #e8eaed;
        color: #6B7280;
    }
    .receipt-container .receipt-table td {
        padding: 0.3rem;
        border-bottom: 1px solid #f0f2f5;
    }
    .receipt-container .receipt-table .text-right {
        text-align: right;
    }
    .receipt-container .receipt-table .text-center {
        text-align: center;
    }
    .receipt-container .receipt-totals {
        border-top: 2px solid #e8eaed;
        margin-top: 10px;
        padding-top: 10px;
    }
    .receipt-container .receipt-totals .total-row {
        display: flex;
        justify-content: space-between;
        padding: 0.2rem 0;
        font-size: 0.9rem;
    }
    .receipt-container .receipt-totals .total-row.final {
        font-size: 1.1rem;
        font-weight: 700;
        color: #002B5C;
        border-top: 2px solid #002B5C;
        padding-top: 0.5rem;
        margin-top: 0.3rem;
    }
    .receipt-container .receipt-rewards {
        color: #28a745;
        font-weight: 600;
        margin: 8px 0;
        text-align: right;
        font-size: 0.85rem;
    }
    .receipt-container .receipt-footer {
        text-align: center;
        font-size: 0.65rem;
        color: #6B7280;
        border-top: 1px solid #e8eaed;
        padding-top: 8px;
        margin-top: 8px;
    }
    
    .auto-refresh-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    .auto-refresh-indicator.active { background: #28a745; }
    .auto-refresh-indicator.inactive { background: #dc3545; }
    
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(0.8); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    @media (max-width: 1200px) {
        .metric-grid { grid-template-columns: repeat(2, 1fr); }
        .quick-actions { grid-template-columns: repeat(3, 1fr); }
        .content-grid { grid-template-columns: 1fr; }
    }
    
    @media (max-width: 768px) {
        .metric-grid { grid-template-columns: 1fr; }
        .quick-actions { grid-template-columns: repeat(2, 1fr); }
        .login-card-tight { padding: 1.5rem; }
        .item-row { grid-template-columns: 1fr 0.8fr; }
        .block-container { padding: 0.5rem !important; }
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# EMAIL CONFIGURATION
# ============================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "gomoraefesto97@gmail.com"
SENDER_PASSWORD = "picz cijg kgbw zoup"
ADMIN_EMAIL = "gomoraefesto97@gmail.com"

# ============================================
# CHECK SECRETS
# ============================================
if 'WEBHOOK_URL' not in st.secrets:
    st.markdown("""
    <div class="login-centered">
        <div class="login-card-tight">
            <div class="spar-logo-small">
                <span class="logo-icon">SPAR</span>
                <span class="logo-text">Dynamics 365</span>
            </div>
            <div class="signin-text-tight">Configuration Required</div>
            <div class="version-info-tight">Please set up your ETL receiver URL</div>
            <div style="background: #f1f5f9; padding: 0.75rem; border-radius: 8px; text-align: left; margin-top: 0.75rem; font-size: 0.7rem;">
                <strong>How to configure:</strong><br><br>
                1. Go to Settings → Secrets<br>
                2. Add: <code>WEBHOOK_URL = "https://your-tunnel.trycloudflare.com/webhook"</code><br>
                3. Replace with your actual tunnel URL<br>
                4. Click Save and Restart
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ============================================
# URL CONFIGURATION
# ============================================
WEBHOOK_URL = st.secrets['WEBHOOK_URL']
BASE_URL = WEBHOOK_URL.replace('/webhook', '')

def api_url(endpoint):
    """Build full API URL from endpoint path"""
    return f"{BASE_URL}{endpoint}"

# ============================================
# USER STORAGE
# ============================================
def get_users_file():
    return Path("users_data.json")

def get_all_users():
    users_file = get_users_file()
    if users_file.exists():
        try:
            with open(users_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_user(email, name, username, password_hash, role):
    users = get_all_users()
    users[email] = {
        'name': name,
        'email': email,
        'username': username,
        'password': password_hash,
        'role': role,
        'created_at': datetime.now().isoformat(),
        'created_by': st.session_state.get('current_user', {}).get('name', 'system') if st.session_state.get('current_user') else 'system'
    }
    with open(get_users_file(), 'w') as f:
        json.dump(users, f, indent=2)
    return True

def init_default_admin():
    users = get_all_users()
    admin_exists = False
    for email, user in users.items():
        if user.get('role') == 'admin':
            admin_exists = True
            break
    if not admin_exists:
        save_user("admin@spar.com", "System Administrator", "admin", hash_password("Admin@123"), "admin")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def register_user(name, username, email, password, role="operator"):
    users = get_all_users()
    if email in users:
        return False, "Email already registered"
    for user_email, user_data in users.items():
        if user_data['username'] == username:
            return False, "Username already taken"
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format"
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    password_hash = hash_password(password)
    save_user(email, name, username, password_hash, role)
    return True, f"User {name} created successfully!"

def login_user(username_or_email, password):
    users = get_all_users()
    for email, user in users.items():
        if user['username'] == username_or_email or email == username_or_email:
            if verify_password(password, user['password']):
                st.session_state.logged_in = True
                st.session_state.current_user = user
                return True, f"Welcome back, {user['name']}!"
    return False, "Invalid username or password"

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None

# Initialize
init_default_admin()

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'sales_history' not in st.session_state:
    st.session_state.sales_history = []
if 'products' not in st.session_state:
    st.session_state.products = []
if 'sales_orders' not in st.session_state:
    st.session_state.sales_orders = []
if 'purchase_orders' not in st.session_state:
    st.session_state.purchase_orders = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True

# ============================================
# API FUNCTIONS
# ============================================

def check_connection():
    """Check if the ETL server is reachable"""
    try:
        url = api_url("/health")
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def fetch_products():
    """Get all products from the database"""
    try:
        url = api_url("/products")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_sales_orders():
    """Get all sales orders"""
    try:
        url = api_url("/sales-orders")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_purchase_orders():
    """Get all purchase orders"""
    try:
        url = api_url("/purchase-orders")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_recent_sales():
    """Get recent sales"""
    try:
        url = api_url("/recent")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def fetch_cash_balance():
    """Get cash balance"""
    try:
        url = api_url("/dynamic-cash-balance")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"cash_balance": 0, "available_cash": 0}
    except:
        return {"cash_balance": 0, "available_cash": 0}

def fetch_overdue_pos():
    """Get overdue PO count"""
    try:
        url = api_url("/overdue-pos")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"overdue_count": 0}
    except:
        return {"overdue_count": 0}

def fetch_incoming_documents():
    """Get incoming documents count"""
    try:
        url = api_url("/incoming-documents")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"count": 0}
    except:
        return {"count": 0}

def fetch_pending_approvals():
    """Get pending approvals"""
    try:
        url = api_url("/pending-approvals")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"pending_pos": 0, "pending_sos": 0}
    except:
        return {"pending_pos": 0, "pending_sos": 0}

def fetch_unprocessed_payments():
    """Get unprocessed payments count"""
    try:
        url = api_url("/unprocessed-payments")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"count": 0}
    except:
        return {"count": 0}

def create_sale(sale_data):
    """Create a new sales order"""
    try:
        url = api_url("/sales-orders")
        response = requests.post(url, json=sale_data, timeout=15)
        if response.status_code == 200:
            return response.json(), None
        try:
            error = response.json()
            return None, error.get('error', f"Server error: {response.status_code}")
        except:
            return None, f"Server error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to ETL server. Please check your connection."
    except requests.exceptions.Timeout:
        return None, "Connection timeout. Server is slow or unreachable."
    except Exception as e:
        return None, str(e)

def add_product(product_data):
    """Add a new product"""
    try:
        url = api_url("/products/add")
        response = requests.post(url, json=product_data, timeout=10)
        if response.status_code == 200:
            return response.json(), None
        try:
            error = response.json()
            return None, error.get('error', f"Server error: {response.status_code}")
        except:
            return None, f"Server error: {response.status_code}"
    except Exception as e:
        return None, str(e)

def create_purchase_order(po_data):
    """Create a new purchase order"""
    try:
        url = api_url("/purchase-orders")
        response = requests.post(url, json=po_data, timeout=15)
        if response.status_code == 200:
            return response.json(), None
        try:
            error = response.json()
            return None, error.get('error', f"Server error: {response.status_code}")
        except:
            return None, f"Server error: {response.status_code}"
    except Exception as e:
        return None, str(e)

def receive_goods(receipt_data):
    """Receive goods for a PO"""
    try:
        url = api_url("/goods-receipt")
        response = requests.post(url, json=receipt_data, timeout=15)
        if response.status_code == 200:
            return response.json(), None
        try:
            error = response.json()
            return None, error.get('error', f"Server error: {response.status_code}")
        except:
            return None, f"Server error: {response.status_code}"
    except Exception as e:
        return None, str(e)

def approve_po(po_number):
    """Approve a purchase order"""
    try:
        url = api_url(f"/purchase-orders/{po_number}/approve")
        response = requests.post(url, timeout=10)
        if response.status_code == 200:
            return response.json(), None
        return None, f"Server error: {response.status_code}"
    except Exception as e:
        return None, str(e)

def reject_po(po_number):
    """Reject a purchase order"""
    try:
        url = api_url(f"/purchase-orders/{po_number}/reject")
        response = requests.post(url, timeout=10)
        if response.status_code == 200:
            return response.json(), None
        return None, f"Server error: {response.status_code}"
    except Exception as e:
        return None, str(e)

def delete_po(po_number):
    """Delete an empty purchase order"""
    try:
        url = api_url(f"/purchase-orders/{po_number}")
        response = requests.delete(url, timeout=10)
        if response.status_code == 200:
            return response.json(), None
        try:
            error = response.json()
            return None, error.get('error', f"Server error: {response.status_code}")
        except:
            return None, f"Server error: {response.status_code}"
    except Exception as e:
        return None, str(e)

def fetch_receipt(order_number):
    """Get receipt for an order"""
    try:
        url = api_url(f"/receipt/{order_number}")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json(), None
        return None, f"Server error: {response.status_code}"
    except Exception as e:
        return None, str(e)

def fetch_po_lines(po_number):
    """Get purchase order lines"""
    try:
        url = api_url(f"/purchase-orders/{po_number}/lines")
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json(), None
        return [], None
    except:
        return [], None

def send_admin_notification(customer_name, sale_id, product, quantity, total_sales, rewards_earned, customer_email=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = ADMIN_EMAIL
        msg['Subject'] = f"NEW SALE - {sale_id}"
        
        recorded_by = st.session_state.current_user['name'] if st.session_state.current_user else 'Unknown'
        
        formatted_total = f"${total_sales:,.2f}"
        formatted_rewards = f"{rewards_earned:.0f}"
        
        html_content = f"""
        <html>
        <body style="font-family: 'Inter', Arial, sans-serif;">
            <h2 style="color: #0052A5;">New SPAR Sale Recorded!</h2>
            <p><strong>Sale ID:</strong> {sale_id}</p>
            <p><strong>Customer:</strong> {customer_name}</p>
            <p><strong>Email:</strong> {customer_email if customer_email else 'Not provided'}</p>
            <p><strong>Product:</strong> {product}</p>
            <p><strong>Quantity:</strong> {quantity}</p>
            <p><strong>Total:</strong> {formatted_total}</p>
            <p><strong>Rewards:</strong> {formatted_rewards} points</p>
            <p><strong>Recorded by:</strong> {recorded_by}</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

# ============================================
# HELPER FUNCTIONS
# ============================================
def format_currency(amount):
    try:
        return f"${float(amount):,.2f}"
    except:
        return "$0.00"

def format_date(date_str):
    if not date_str:
        return "N/A"
    try:
        dt = pd.to_datetime(date_str)
        return dt.strftime('%Y-%m-%d')
    except:
        return str(date_str)

def get_stock_status(stock, reorder):
    if stock is None:
        return "out-of-stock"
    try:
        stock = float(stock)
        reorder = float(reorder) if reorder else 10
        if stock <= 0:
            return "out-of-stock"
        elif stock <= reorder:
            return "low-stock"
        else:
            return "in-stock"
    except:
        return "in-stock"

def get_stock_label(stock, reorder):
    status = get_stock_status(stock, reorder)
    labels = {
        'in-stock': 'In Stock',
        'low-stock': 'Low Stock',
        'out-of-stock': 'Out of Stock'
    }
    return labels.get(status, 'Unknown')

def get_stock_color(stock, reorder):
    status = get_stock_status(stock, reorder)
    colors = {
        'in-stock': '#28a745',
        'low-stock': '#f39c12',
        'out-of-stock': '#dc3545'
    }
    return colors.get(status, '#6B7280')

def load_all_data():
    """Load all data from the API"""
    st.session_state.products = fetch_products()
    st.session_state.sales_orders = fetch_sales_orders()
    st.session_state.purchase_orders = fetch_purchase_orders()

# ============================================
# LOGIN SCREEN
# ============================================
def login_screen():
    st.markdown("""
    <div class="login-centered">
        <div class="login-card-tight">
            <div class="spar-logo-small">
                <span class="logo-icon">SPAR</span>
                <span class="logo-text">Dynamics 365</span>
            </div>
            <div class="signin-text-tight">Enterprise Resource Planning</div>
            <div class="version-info-tight">Version 3.5.0 - Production</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("Sign In", use_container_width=True)
        
        if submitted:
            if username and password:
                success, message = login_user(username, password)
                if success:
                    st.success(message)
                    load_all_data()
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter your username and password")
    
    st.markdown("""
        <div style="margin-top: 1rem; font-size: 0.65rem; color: #9AA0A6;">
            Default: admin / Admin@123
        </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN APP INTERFACE
# ============================================
def main_app_interface():
    user_name = st.session_state.current_user['name']
    user_role = st.session_state.current_user['role']
    is_admin = (user_role == 'admin')
    
    if is_admin:
        st.markdown("""
        <div class="modern-header">
            <h1>🛒 Admin Dashboard</h1>
            <p>Complete control over sales, products, and purchase orders</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="modern-header">
            <h1>🛒 Operator Dashboard</h1>
            <p>Record sales and view your daily performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="nav-bar">
        <div class="logo-area">
            <span style="font-size: 1rem;">🏢</span>
            <span class="logo-text">SPAR Dynamics 365</span>
        </div>
        <div class="user-area">
            <span class="role-badge">{user_role.upper()}</span>
            <span class="user-name-badge">{user_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ETL Status
    col1, col2 = st.columns([3, 1])
    with col1:
        if check_connection():
            st.success("✅ ETL Connected - Data is being synced with database")
        else:
            st.error("❌ ETL Offline - Cannot connect to server")
    with col2:
        if st.button("Sign Out", key="signout"):
            logout_user()
            st.rerun()
    
    if is_admin:
        admin_view()
    else:
        operator_view()

# ============================================
# OPERATOR VIEW
# ============================================
def operator_view():
    user_name = st.session_state.current_user['name']
    
    tab1, tab2 = st.tabs(["📝 Record Sale", "📊 My Sales"])
    
    with tab1:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📋 New Purchase</div>', unsafe_allow_html=True)
            
            # Customer Details
            col_a, col_b = st.columns(2)
            with col_a:
                customer_name = st.text_input("Customer Name *", placeholder="Enter full name")
            with col_b:
                customer_email = st.text_input("Email Address", placeholder="customer@example.com")
            
            st.markdown("---")
            st.markdown('<p style="color: #202124; font-weight: 600;">🛍️ Purchase Details</p>', unsafe_allow_html=True)
            
            # Product Selection
            products = st.session_state.products
            if products:
                product_options = {f"{p.get('product_code', '')} - {p.get('product_name', '')}": p.get('id') for p in products}
                selected_product = st.selectbox("Product", list(product_options.keys()))
                product_id = product_options.get(selected_product)
                
                # Get product details
                selected_product_data = next((p for p in products if p.get('id') == product_id), None)
                
                col_e, col_f = st.columns(2)
                with col_e:
                    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                with col_f:
                    default_price = selected_product_data.get('unit_price', 0) if selected_product_data else 0
                    unit_price = st.number_input("Unit Price (USD)", min_value=0.01, value=float(default_price), step=0.01, format="%.2f")
                
                total_sales = quantity * unit_price
                st.metric("Total Amount", f"${total_sales:,.2f}")
                st.caption(f"📅 Purchase Date: {datetime.now().strftime('%m/%d/%Y')}")
                
                rewards_earned = total_sales * 0.02
                st.info(f"⭐ Rewards Points Earned: {rewards_earned:.0f} (2% of purchase)")
                
                submitted = st.button("💾 Record Sale", use_container_width=True)
                
                if submitted:
                    if not customer_name:
                        st.error("Please enter customer name")
                    elif not product_id:
                        st.error("Please select a product")
                    else:
                        sale_data = {
                            "customer_name": customer_name,
                            "customer_email": customer_email if customer_email else "",
                            "items": [{
                                "product_id": product_id,
                                "quantity": quantity,
                                "unit_price": unit_price
                            }],
                            "recorded_by": user_name
                        }
                        
                        result, error = create_sale(sale_data)
                        if result:
                            st.success(f"✅ Sale recorded! Order: {result.get('order_number')} | Total: ${result.get('total_amount', 0):,.2f}")
                            st.balloons()
                            if result.get('rewards_earned'):
                                st.info(f"⭐ Rewards Earned: {result.get('rewards_earned'):.2f} pts")
                            send_admin_notification(customer_name, result.get('order_number'), selected_product, quantity, total_sales, rewards_earned, customer_email)
                            load_all_data()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"❌ {error}")
            else:
                st.warning("No products found in database. Please contact administrator.")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📊 System Status</div>', unsafe_allow_html=True)
            
            if check_connection():
                st.success("✅ ETL Connected")
                st.info("📤 Data is being sent to database")
            else:
                st.warning("⚠️ ETL Offline - Tunnel may be down")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-header">📊 My Sales - {user_name}</div>', unsafe_allow_html=True)
        
        recent_sales = fetch_recent_sales()
        user_sales = [s for s in recent_sales if s.get('recorded_by') == user_name]
        
        if user_sales:
            df = pd.DataFrame(user_sales)
            total_revenue = df['total_sales'].sum() if 'total_sales' in df.columns else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Transactions", len(df))
            with col2:
                st.metric("Revenue", f"${total_revenue:,.2f}")
            with col3:
                avg_sale = df['total_sales'].mean() if 'total_sales' in df.columns else 0
                st.metric("Average Sale", f"${avg_sale:.2f}")
            with col4:
                customers = df['customer_name'].nunique() if 'customer_name' in df.columns else 0
                st.metric("Customers Served", customers)
            
            st.markdown("#### Sales Details")
            display_cols = ['sale_id', 'customer_name', 'total_sales', 'sale_time']
            available_cols = [c for c in display_cols if c in df.columns]
            if available_cols:
                st.dataframe(df[available_cols], use_container_width=True, height=300)
        else:
            st.info("No sales recorded. Start selling!")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# ADMIN VIEW
# ============================================
def admin_view():
    user_name = st.session_state.current_user['name']
    
    # Load data
    if not st.session_state.products:
        load_all_data()
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Dashboard", "📝 Record Sale", "📋 Sales Orders", 
        "📦 Purchase Orders", "📥 Products", "⚙️ Admin Panel"
    ])
    
    with tab1:
        render_dashboard()
    
    with tab2:
        render_sale_form_admin()
    
    with tab3:
        render_sales_orders()
    
    with tab4:
        render_purchase_orders()
    
    with tab5:
        render_products()
    
    with tab6:
        render_admin_panel()

# ============================================
# DASHBOARD
# ============================================
def render_dashboard():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📊 Business Overview</div>', unsafe_allow_html=True)
    
    # Fetch data
    recent_sales = fetch_recent_sales()
    products = st.session_state.products
    purchase_orders = st.session_state.purchase_orders
    
    # Calculate metrics
    today = datetime.now().date()
    today_sales = [s for s in recent_sales if pd.to_datetime(s.get('sale_date', '')).date() == today] if recent_sales else []
    total_revenue = sum(float(s.get('total_sales', 0)) for s in today_sales)
    transaction_count = len(today_sales)
    
    total_products = len(products) if products else 0
    low_stock = sum(1 for p in products if get_stock_status(p.get('current_stock'), p.get('reorder_level')) == 'low-stock') if products else 0
    out_of_stock = sum(1 for p in products if get_stock_status(p.get('current_stock'), p.get('reorder_level')) == 'out-of-stock') if products else 0
    
    pending_pos = len([p for p in purchase_orders if p.get('status') not in ['Received', 'Cancelled']]) if purchase_orders else 0
    
    # Cash balance
    cash_data = fetch_cash_balance()
    cash_balance = cash_data.get('available_cash', 0)
    
    # Overdue POs
    overdue = fetch_overdue_pos()
    overdue_count = overdue.get('overdue_count', 0)
    
    # Incoming docs
    incoming = fetch_incoming_documents()
    incoming_count = incoming.get('count', 0)
    
    # Pending approvals
    pending = fetch_pending_approvals()
    pending_pos_count = pending.get('pending_pos', 0)
    pending_sos_count = pending.get('pending_sos', 0)
    
    # Unprocessed payments
    unprocessed = fetch_unprocessed_payments()
    unprocessed_count = unprocessed.get('count', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Today's Revenue", f"${total_revenue:,.2f}", f"{transaction_count} transactions")
    with col2:
        st.metric("📦 Total Products", total_products, f"{low_stock} low stock, {out_of_stock} out of stock")
    with col3:
        st.metric("📋 Pending POs", pending_pos, "Awaiting delivery" if pending_pos > 0 else "All received")
    with col4:
        st.metric("🏦 Cash Balance", f"${cash_balance:,.2f}")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Overdue POs", overdue_count, "Past due date" if overdue_count > 0 else "All current")
    with col2:
        st.metric("📄 Incoming Docs", incoming_count, "Pending processing" if incoming_count > 0 else "None pending")
    with col3:
        st.metric("⏳ Pending Approvals", f"{pending_pos_count} POs, {pending_sos_count} SOs")
    with col4:
        st.metric("💳 Unprocessed Payments", unprocessed_count, "Awaiting processing" if unprocessed_count > 0 else "All processed")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("""
    <div class="quick-actions">
        <div class="quick-action" onclick="window.location.href='?page=sale'">
            <i class="fas fa-shopping-cart"></i>
            <span class="label">New Sale</span>
        </div>
        <div class="quick-action" onclick="window.location.href='?page=po'">
            <i class="fas fa-truck"></i>
            <span class="label">New PO</span>
        </div>
        <div class="quick-action" onclick="window.location.href='?page=products'">
            <i class="fas fa-boxes"></i>
            <span class="label">Products</span>
        </div>
        <div class="quick-action" onclick="window.location.href='?page=orders'">
            <i class="fas fa-file-invoice"></i>
            <span class="label">Sales Orders</span>
        </div>
        <div class="quick-action" onclick="window.location.href='?page=purchase'">
            <i class="fas fa-list"></i>
            <span class="label">Purchase Orders</span>
        </div>
        <div class="quick-action" onclick="window.location.reload()">
            <i class="fas fa-sync"></i>
            <span class="label">Refresh</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sales Trend
    if recent_sales:
        df = pd.DataFrame(recent_sales)
        if 'sale_date' in df.columns and 'total_sales' in df.columns:
            df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
            daily_sales = df.groupby('sale_date')['total_sales'].sum().reset_index()
            daily_sales = daily_sales.sort_values('sale_date').tail(7)
            
            if len(daily_sales) > 0:
                fig = px.line(daily_sales, x='sale_date', y='total_sales', 
                              title="📈 Sales Trend (Last 7 Days)", markers=True,
                              color_discrete_sequence=['#0052A5'])
                fig.update_layout(height=300, plot_bgcolor='white', paper_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
    
    # Recent Orders
    if recent_sales:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📋 Recent Orders</div>', unsafe_allow_html=True)
        
        recent = recent_sales[:5]
        for sale in recent:
            customer = sale.get('customer_name', 'Unknown')
            sale_id = sale.get('sale_id', 'N/A')
            total = sale.get('total_sales', 0)
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:0.3rem 0;border-bottom:1px solid #f0f2f5;">
                <div>
                    <strong>{sale_id}</strong>
                    <span style="color:#6B7280;font-size:0.8rem;margin-left:0.5rem;">{customer}</span>
                </div>
                <div>
                    <span style="font-weight:600;">${total:,.2f}</span>
                    <span class="status-badge synced" style="margin-left:0.5rem;">Synced</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SALE FORM (ADMIN)
# ============================================
def render_sale_form_admin():
    user_name = st.session_state.current_user['name']
    
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📋 New Purchase</div>', unsafe_allow_html=True)
    
    # Customer Details
    col_a, col_b = st.columns(2)
    with col_a:
        customer_name = st.text_input("Customer Name *", placeholder="Enter full name")
    with col_b:
        customer_email = st.text_input("Email Address", placeholder="customer@example.com")
    
    st.markdown("---")
    st.markdown('<p style="color: #202124; font-weight: 600;">🛍️ Purchase Details</p>', unsafe_allow_html=True)
    
    # Product Selection
    products = st.session_state.products
    if products:
        product_options = {f"{p.get('product_code', '')} - {p.get('product_name', '')}": p.get('id') for p in products}
        selected_product = st.selectbox("Product", list(product_options.keys()))
        product_id = product_options.get(selected_product)
        
        selected_product_data = next((p for p in products if p.get('id') == product_id), None)
        
        col_e, col_f = st.columns(2)
        with col_e:
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
        with col_f:
            default_price = selected_product_data.get('unit_price', 0) if selected_product_data else 0
            unit_price = st.number_input("Unit Price (USD)", min_value=0.01, value=float(default_price), step=0.01, format="%.2f")
        
        total_sales = quantity * unit_price
        st.metric("Total Amount", f"${total_sales:,.2f}")
        st.caption(f"📅 Purchase Date: {datetime.now().strftime('%m/%d/%Y')}")
        
        rewards_earned = total_sales * 0.02
        st.info(f"⭐ Rewards Points Earned: {rewards_earned:.0f} (2% of purchase)")
        
        submitted = st.button("💾 Record Sale", use_container_width=True)
        
        if submitted:
            if not customer_name:
                st.error("Please enter customer name")
            elif not product_id:
                st.error("Please select a product")
            else:
                sale_data = {
                    "customer_name": customer_name,
                    "customer_email": customer_email if customer_email else "",
                    "items": [{
                        "product_id": product_id,
                        "quantity": quantity,
                        "unit_price": unit_price
                    }],
                    "recorded_by": user_name
                }
                
                result, error = create_sale(sale_data)
                if result:
                    st.success(f"✅ Sale recorded! Order: {result.get('order_number')} | Total: ${result.get('total_amount', 0):,.2f}")
                    st.balloons()
                    if result.get('rewards_earned'):
                        st.info(f"⭐ Rewards Earned: {result.get('rewards_earned'):.2f} pts")
                    send_admin_notification(customer_name, result.get('order_number'), selected_product, quantity, total_sales, rewards_earned, customer_email)
                    load_all_data()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {error}")
    else:
        st.warning("No products found in database. Please add products first.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# SALES ORDERS
# ============================================
def render_sales_orders():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📋 Sales Orders</div>', unsafe_allow_html=True)
    
    orders = st.session_state.sales_orders
    
    if orders:
        df = pd.DataFrame(orders)
        
        # Filter
        search = st.text_input("🔍 Search by customer or order #", "")
        if search:
            df = df[df['customer_name'].str.contains(search, case=False, na=False) | 
                    df['order_number'].str.contains(search, case=False, na=False)]
        
        st.dataframe(df, use_container_width=True, height=400)
        
        # Receipt button
        if 'order_number' in df.columns:
            selected_order = st.selectbox("Generate Receipt", ["Select Order"] + df['order_number'].tolist())
            if selected_order != "Select Order":
                if st.button("🧾 View Receipt"):
                    receipt, error = fetch_receipt(selected_order)
                    if receipt:
                        render_receipt(receipt)
                    else:
                        st.error(f"Failed to load receipt: {error}")
    else:
        st.info("No sales orders found")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# RECEIPT
# ============================================
def render_receipt(receipt_data):
    if receipt_data.get('status') == 'success':
        receipt = receipt_data.get('receipt', {})
        
        st.markdown(f"""
        <div class="receipt-container">
            <div class="receipt-header">
                <h2>SPAR Dynamics 365</h2>
                <p>Yellowcob Enterprises Pvt Ltd</p>
                <hr>
            </div>
            <div class="receipt-info">
                <span class="label">Order #:</span>
                <span>{receipt.get('order_number', 'N/A')}</span>
                <span class="label">Date:</span>
                <span>{receipt.get('order_date', 'N/A')}</span>
                <span class="label">Time:</span>
                <span>{receipt.get('order_time', 'N/A')}</span>
                <span class="label">Customer:</span>
                <span>{receipt.get('customer_name', 'N/A')}</span>
            </div>
            <hr>
            <table class="receipt-table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th class="text-center">Qty</th>
                        <th class="text-right">Price</th>
                        <th class="text-right">Total</th>
                    </tr>
                </thead>
                <tbody>
        """, unsafe_allow_html=True)
        
        for item in receipt.get('lines', []):
            st.markdown(f"""
            <tr>
                <td>{item.get('product_name', 'Unknown')}</td>
                <td class="text-center">{item.get('quantity', 0)}</td>
                <td class="text-right">${item.get('unit_price', 0):.2f}</td>
                <td class="text-right">${item.get('line_total', 0):.2f}</td>
            </tr>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
                </tbody>
            </table>
            <div class="receipt-totals">
                <div class="total-row final">
                    <span>Total Amount:</span>
                    <span style="font-weight:700;font-size:1.2rem;">${receipt.get('total_amount', 0):.2f}</span>
                </div>
            </div>
            <div class="receipt-rewards">
                ⭐ Rewards Earned: {receipt.get('rewards_earned', 0):.2f} pts
            </div>
            <div class="receipt-footer">
                <p>Thank you for shopping with SPAR!</p>
                <p style="font-size:0.6rem;">Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# PURCHASE ORDERS
# ============================================
def render_purchase_orders():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📦 Purchase Orders</div>', unsafe_allow_html=True)
    
    # Create PO button
    with st.expander("➕ Create New Purchase Order"):
        with st.form("create_po_form"):
            col1, col2 = st.columns(2)
            with col1:
                supplier_name = st.text_input("Supplier Name *")
            with col2:
                supplier_email = st.text_input("Supplier Email")
            
            expected_date = st.date_input("Expected Delivery Date", min_value=datetime.now().date())
            
            st.markdown("#### Order Items")
            items = []
            num_items = st.number_input("Number of Items", min_value=1, max_value=10, value=1)
            
            for i in range(num_items):
                st.markdown(f"**Item {i+1}**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    product_options = {f"{p.get('product_code', '')} - {p.get('product_name', '')}": p.get('id') for p in st.session_state.products}
                    selected = st.selectbox(f"Product", list(product_options.keys()), key=f"po_prod_{i}")
                    product_id = product_options.get(selected)
                with col2:
                    qty = st.number_input(f"Quantity", min_value=1, value=1, key=f"po_qty_{i}")
                with col3:
                    price = st.number_input(f"Unit Price", min_value=0.01, value=0.00, key=f"po_price_{i}")
                
                items.append({
                    "product_id": product_id,
                    "quantity": qty,
                    "unit_price": price
                })
            
            submitted = st.form_submit_button("📦 Create Purchase Order", use_container_width=True)
            
            if submitted:
                if not supplier_name:
                    st.error("Please enter supplier name")
                elif not all(i.get('product_id') and i.get('quantity') and i.get('unit_price') for i in items):
                    st.error("Please fill all item details")
                else:
                    po_data = {
                        "supplier_name": supplier_name,
                        "supplier_email": supplier_email,
                        "expected_delivery_date": expected_date.strftime('%Y-%m-%d'),
                        "items": items,
                        "created_by": user_name
                    }
                    
                    result, error = create_purchase_order(po_data)
                    if result:
                        st.success(f"✅ Purchase Order {result.get('po_number')} created!")
                        load_all_data()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
    
    # View POs
    pos = st.session_state.purchase_orders
    
    if pos:
        df = pd.DataFrame(pos)
        st.dataframe(df, use_container_width=True, height=400)
        
        # Actions
        st.markdown("#### Actions")
        selected_po = st.selectbox("Select PO", ["Select PO"] + df['po_number'].tolist() if 'po_number' in df.columns else [])
        
        if selected_po != "Select PO":
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👍 Approve PO"):
                    result, error = approve_po(selected_po)
                    if result:
                        st.success(f"✅ PO {selected_po} approved!")
                        load_all_data()
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
            
            with col2:
                if st.button("👎 Reject PO"):
                    result, error = reject_po(selected_po)
                    if result:
                        st.success(f"✅ PO {selected_po} rejected!")
                        load_all_data()
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
            
            with col3:
                if st.button("🗑️ Delete Empty PO"):
                    result, error = delete_po(selected_po)
                    if result:
                        st.success(f"✅ PO {selected_po} deleted!")
                        load_all_data()
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
            
            # View PO lines
            if st.button("📋 View PO Lines"):
                lines, error = fetch_po_lines(selected_po)
                if lines:
                    st.dataframe(pd.DataFrame(lines), use_container_width=True)
                else:
                    st.info("No items found for this PO")
    else:
        st.info("No purchase orders found")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# PRODUCTS
# ============================================
def render_products():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📦 Product Management</div>', unsafe_allow_html=True)
    
    # Add Product
    with st.expander("➕ Add New Product"):
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            with col1:
                product_code = st.text_input("Product Code *")
                product_name = st.text_input("Product Name *")
                category_name = st.text_input("Category *")
            with col2:
                unit_price = st.number_input("Unit Price (USD)", min_value=0.01, value=0.01, step=0.01)
                initial_stock = st.number_input("Initial Stock", min_value=0, value=0, step=1)
                reorder_level = st.number_input("Reorder Level", min_value=1, value=10, step=1)
            
            submitted = st.form_submit_button("💾 Add Product", use_container_width=True)
            
            if submitted:
                if not product_code or not product_name or not category_name:
                    st.error("Please fill all required fields")
                else:
                    product_data = {
                        "product_code": product_code,
                        "product_name": product_name,
                        "category_name": category_name,
                        "unit_price": unit_price,
                        "initial_stock": initial_stock,
                        "reorder_level": reorder_level,
                        "created_by": user_name
                    }
                    
                    result, error = add_product(product_data)
                    if result:
                        st.success(f"✅ Product {product_name} added successfully!")
                        load_all_data()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
    
    # View Products
    products = st.session_state.products
    
    if products:
        df = pd.DataFrame(products)
        
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            search = st.text_input("🔍 Search by name or code", "")
        with col2:
            if 'category_name' in df.columns:
                categories = ["All"] + df['category_name'].unique().tolist()
                category_filter = st.selectbox("Filter by Category", categories)
        
        # Apply filters
        if search:
            df = df[df['product_name'].str.contains(search, case=False, na=False) | 
                    df['product_code'].str.contains(search, case=False, na=False)]
        if 'category_filter' in locals() and category_filter != "All":
            df = df[df['category_name'] == category_filter]
        
        # Display products
        for _, product in df.iterrows():
            stock = product.get('current_stock', 0)
            reorder = product.get('reorder_level', 10)
            status = get_stock_status(stock, reorder)
            color = get_stock_color(stock, reorder)
            label = get_stock_label(stock, reorder)
            
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem;border-bottom:1px solid #f0f2f5;">
                <div>
                    <strong>{product.get('product_name', 'Unknown')}</strong>
                    <span style="color:#6B7280;font-size:0.8rem;margin-left:0.5rem;">{product.get('product_code', '')}</span>
                    <span style="color:#6B7280;font-size:0.7rem;margin-left:0.5rem;background:#f0f2f5;padding:0.1rem 0.5rem;border-radius:12px;">
                        {product.get('category_name', 'Uncategorized')}
                    </span>
                </div>
                <div>
                    <span style="font-weight:600;color:{color};">{stock}</span>
                    <span style="color:#6B7280;font-size:0.7rem;margin-left:0.5rem;">({label})</span>
                    <span style="color:#6B7280;font-size:0.7rem;margin-left:0.5rem;">${product.get('unit_price', 0):.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No products found in database")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# ADMIN PANEL
# ============================================
def render_admin_panel():
    st.markdown('<div class="modern-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">⚙️ Admin Control Panel</div>', unsafe_allow_html=True)
    
    # Create User
    st.markdown("#### 👤 Create New User")
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name *")
            new_username = st.text_input("Username *")
        with col2:
            new_email = st.text_input("Email *")
            new_password = st.text_input("Password *", type="password")
            new_role = st.selectbox("Role", ["operator", "admin"])
        
        submitted = st.form_submit_button("👤 Create User", use_container_width=True)
        
        if submitted:
            if not all([new_name, new_username, new_email, new_password]):
                st.error("Please fill all fields")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, message = register_user(new_name, new_username, new_email, new_password, new_role)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    st.markdown("---")
    
    # Existing Users
    st.markdown("#### 👥 Existing Users")
    users = get_all_users()
    if users:
        users_list = []
        for email, u in users.items():
            users_list.append({
                'Name': u['name'],
                'Email': email,
                'Username': u['username'],
                'Role': 'ADMIN' if u['role'] == 'admin' else 'OPERATOR',
                'Created': u.get('created_at', '')[:10]
            })
        st.dataframe(pd.DataFrame(users_list), use_container_width=True)
    
    st.markdown("---")
    
    # System Status
    st.markdown("#### 📊 System Status")
    if check_connection():
        st.success("✅ ETL Server Connected")
    else:
        st.error("❌ ETL Server Offline")
    
    st.markdown("---")
    
    # Configuration
    st.markdown("#### 🔧 Configuration")
    st.code(f"WEBHOOK_URL = {WEBHOOK_URL}", language="python")
    st.code(f"BASE_URL = {BASE_URL}", language="python")
    
    st.markdown("---")
    
    # Refresh Data
    if st.button("🔄 Refresh All Data", use_container_width=True):
        load_all_data()
        st.success("✅ Data refreshed!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN
# ============================================
if st.session_state.logged_in:
    user_name = st.session_state.current_user.get('name', 'User')
    main_app_interface()
else:
    login_screen()
