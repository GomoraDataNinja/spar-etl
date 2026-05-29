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
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="Tengai - SPAR Sales & Rewards",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# MODERN CENTERED LOGIN CSS
# ============================================
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');
    
    /* Global reset */
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Main app background - Clean gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Remove default padding */
    .block-container {
        padding: 2rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }
    
    /* Centered Login Container */
    .login-centered {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
    }
    
    /* Single Login Card - Clean and simple */
    .login-card-single {
        background: white;
        border-radius: 32px;
        padding: 2.5rem;
        max-width: 400px;
        width: 100%;
        box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25);
        text-align: center;
    }
    
    .login-logo {
        font-size: 3.5rem;
        margin-bottom: 0.75rem;
    }
    
    .login-title {
        font-size: 1.75rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }
    
    .login-subtitle {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-bottom: 1.5rem;
    }
    
    /* Form Styling */
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
        background: #f8fafc;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        background: white;
        box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #94a3b8;
    }
    
    /* Button Container - Center the button */
    .stButton {
        display: flex;
        justify-content: center;
        margin-top: 0.5rem;
    }
    
    /* Button Styling - Small and centered */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 40px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s ease;
        width: auto;
        min-width: 120px;
        margin: 0 auto;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102,126,234,0.4);
    }
    
    /* Version info */
    .version-info {
        margin-top: 1.5rem;
        text-align: center;
        font-size: 0.7rem;
        color: #94a3b8;
    }
    
    /* Divider */
    .divider {
        margin: 1rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Hide default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 12px;
        border: none;
        margin-bottom: 1rem;
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
        <div class="login-card-single">
            <div class="login-logo">🔧</div>
            <div class="login-title">Configuration Required</div>
            <div class="login-subtitle">Please set up your Cloudflare tunnel URL</div>
            <div style="background: #f1f5f9; padding: 1rem; border-radius: 12px; text-align: left;">
                <strong>How to configure:</strong><br><br>
                1. Go to Settings → Secrets<br>
                2. Add: <code>WEBHOOK_URL = "https://your-tunnel-url.trycloudflare.com/webhook"</code><br>
                3. Replace with your actual tunnel URL<br>
                4. Click Save and Restart
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

WEBHOOK_URL = st.secrets['WEBHOOK_URL']

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
        save_user("admin@tengai.com", "Administrator", "admin", hash_password("Admin@123"), "admin")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def register_user(name, username, email, password, role="user"):
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
    return True, f"Operator {name} created successfully!"

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
if 'rewards_df' not in st.session_state:
    st.session_state.rewards_df = None
if 'rfm_data' not in st.session_state:
    st.session_state.rfm_data = None

# ============================================
# APP CONSTANTS
# ============================================
APP_NAME = "Tengai"
APP_VERSION = "3.5.0"

# ============================================
# LOGIN SCREEN - Clean Simple Box
# ============================================
def login_screen():
    st.markdown("""
    <div class="login-centered">
        <div class="login-card-single">
            <div class="login-logo">🛒</div>
            <div class="login-title">Tengai</div>
            <div class="login-subtitle">SPAR Sales & Rewards System</div>
    """, unsafe_allow_html=True)
    
    # Login Form
    with st.form("login_form"):
        username = st.text_input("Username or Email", placeholder="Enter your username or email", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="collapsed")
        
        # Centered button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("Sign In", use_container_width=False)
        
        if submitted and username and password:
            success, message = login_user(username, password)
            if success:
                st.success(message)
                time.sleep(0.5)
                st.rerun()
            else:
                st.error(message)
    
    # Version info
    st.markdown(f"""
            <div class="version-info">
                Version {APP_VERSION} • Production
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# DATABASE QUERY FUNCTIONS
# ============================================

def check_connection():
    try:
        health_url = WEBHOOK_URL.replace('/webhook', '/health')
        response = requests.get(health_url, timeout=5)
        return response.status_code == 200
    except:
        return False

def get_sales_from_db(operator_name=None, date_filter=None, start_date=None, end_date=None):
    try:
        url = WEBHOOK_URL.replace('/webhook', '/recent')
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return []
        
        sales = response.json()
        
        if not sales:
            return []
        
        df = pd.DataFrame(sales)
        
        if 'recorded_by' not in df.columns:
            df['recorded_by'] = 'Unknown'
        
        if 'sale_date' not in df.columns and 'created_at' in df.columns:
            df['sale_date'] = pd.to_datetime(df['created_at']).dt.date
        elif 'sale_date' in df.columns:
            df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
        else:
            df['sale_date'] = datetime.now().date()
        
        if operator_name:
            operator_name_clean = operator_name.strip().lower()
            df = df[df['recorded_by'].astype(str).str.strip().str.lower() == operator_name_clean]
        
        if date_filter == 'today':
            today = datetime.now().date()
            df = df[df['sale_date'] == today]
        elif start_date and end_date:
            df = df[(df['sale_date'] >= start_date) & (df['sale_date'] <= end_date)]
        
        return df.to_dict('records')
    except Exception as e:
        print(f"Error fetching sales: {e}")
        return []

# ============================================
# REWARDS ANALYSIS FUNCTIONS
# ============================================

def calculate_age_group(birthdate):
    if pd.isna(birthdate):
        return "Unknown"
    today = datetime.now()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    if age < 18: return "Under 18"
    elif age < 25: return "18-24"
    elif age < 35: return "25-34"
    elif age < 45: return "35-44"
    elif age < 55: return "45-54"
    elif age < 65: return "55-64"
    else: return "65+"

@st.cache_data
def clean_rewards_data(df):
    df = df.copy()
    df.columns = df.columns.str.lower().str.replace(" ", "_")
    
    if 'member_number' not in df.columns:
        for col in ['member no', 'member', 'customer_id', 'customer']:
            if col in df.columns:
                df.rename(columns={col: 'member_number'}, inplace=True)
                break
    
    if 'redemption_date' not in df.columns:
        for col in ['date', 'transaction_date', 'created_date']:
            if col in df.columns:
                df.rename(columns={col: 'redemption_date'}, inplace=True)
                break
    
    if 'redeeming_basket_value' in df.columns:
        df.rename(columns={'redeeming_basket_value': 'basket_value'}, inplace=True)
    
    if 'basket_value' not in df.columns and 'amount' in df.columns:
        df.rename(columns={'amount': 'basket_value'}, inplace=True)
    
    if 'birthday' in df.columns:
        df['birthday'] = pd.to_datetime(df['birthday'], errors='coerce')
        df['age_group'] = df['birthday'].apply(calculate_age_group)
    else:
        df['age_group'] = "Unknown"
    
    df['redemption_date'] = pd.to_datetime(df['redemption_date'], errors='coerce')
    df['basket_value'] = pd.to_numeric(df['basket_value'], errors='coerce')
    df['year'] = df['redemption_date'].dt.year
    df['month'] = df['redemption_date'].dt.month
    df['day'] = df['redemption_date'].dt.day
    
    df = df[df['basket_value'] > 0]
    df = df[df['member_number'].notna()]
    df = df[df['redemption_date'].notna()]
    
    return df

@st.cache_data
def calculate_rfm(df):
    ref_date = df['redemption_date'].max()
    rfm = df.groupby('member_number').agg(
        recency=('redemption_date', lambda x: (ref_date - x.max()).days),
        frequency=('member_number', 'count'),
        monetary=('basket_value', 'sum'),
        avg_basket=('basket_value', 'mean'),
        age_group=('age_group', 'first')
    )
    return rfm

def segment_customers(rfm):
    rfm['segment'] = 'Other'
    mask_active = (rfm['recency'] <= 30)
    rfm.loc[mask_active, 'segment'] = "Active"
    mask_warming = (rfm['recency'] > 30) & (rfm['recency'] <= 60)
    rfm.loc[mask_warming, 'segment'] = "Warming"
    mask_at_risk = (rfm['recency'] > 60) & (rfm['recency'] <= 90)
    rfm.loc[mask_at_risk, 'segment'] = "At Risk"
    mask_churned = (rfm['recency'] > 90)
    rfm.loc[mask_churned, 'segment'] = "Churned"
    mask_one_time = (rfm['frequency'] == 1) & (rfm['segment'] == 'Other')
    rfm.loc[mask_one_time, 'segment'] = "One-Time"
    return rfm

def calculate_clv(rfm):
    avg_transaction_value = rfm['monetary'] / rfm['frequency'].clip(lower=1)
    avg_frequency_days = rfm['recency'] / rfm['frequency'].clip(lower=1)
    purchase_frequency_per_month = 30 / avg_frequency_days.clip(lower=1)
    rfm['clv'] = avg_transaction_value * purchase_frequency_per_month * 12
    rfm['clv'] = rfm['clv'].fillna(0)
    try:
        rfm['clv_segment'] = pd.qcut(rfm['clv'], q=4, labels=['Bronze', 'Silver', 'Gold', 'Platinum'])
    except:
        rfm['clv_segment'] = 'Standard'
    return rfm

def calculate_churn_probability(rfm):
    max_recency = max(rfm['recency'].max(), 1)
    max_frequency = max(rfm['frequency'].max(), 1)
    max_monetary = max(rfm['monetary'].max(), 1)
    rfm['churn_score'] = (
        (rfm['recency'] / max_recency) * 0.5 +
        (1 - rfm['frequency'] / max_frequency) * 0.3 +
        (1 - rfm['monetary'] / max_monetary) * 0.2
    )
    rfm['churn_risk'] = pd.cut(rfm['churn_score'], 
                                bins=[0, 0.25, 0.5, 0.75, 1], 
                                labels=['Very Low', 'Low', 'Medium', 'High'])
    return rfm

def generate_actions(rfm):
    actions = []
    priorities = []
    for idx, row in rfm.iterrows():
        if row['segment'] == 'At Risk':
            actions.append("URGENT: Send 30% discount + personalized email")
            priorities.append("High")
        elif row['segment'] == 'Warming':
            actions.append("ACT NOW: Send 15% off + engagement email")
            priorities.append("High")
        elif row['segment'] == 'Churned':
            actions.append("Win-back campaign with special offer")
            priorities.append("High")
        elif row['segment'] == 'One-Time':
            actions.append("Welcome back incentive + loyalty program invite")
            priorities.append("Medium")
        elif row['segment'] == 'Active':
            actions.append("Thank you for shopping! Check out our latest offers")
            priorities.append("Low")
        else:
            actions.append("Nurture engagement with regular content")
            priorities.append("Low")
    rfm['recommended_action'] = actions
    rfm['priority'] = priorities
    return rfm

def safe_currency_format(value):
    try:
        if pd.isna(value) or value is None:
            return "$0"
        return f"${float(value):,.0f}"
    except:
        return "$0"

# ============================================
# HELPER FUNCTIONS
# ============================================
def generate_sale_id():
    return f"SPAR-{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}"

def send_to_webhook(data):
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if response.status_code == 200:
            return True, "Data sent to ETL"
        return False, f"Server error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to ETL server (tunnel may be down)"
    except requests.exceptions.Timeout:
        return False, "Connection timeout - ETL server slow"
    except Exception as e:
        return False, str(e)

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
            <h2 style="color: #667eea;">New SPAR Sale Recorded!</h2>
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
# MAIN APP INTERFACE (After Login)
# ============================================
def main_app_interface():
    user_name = st.session_state.current_user['name']
    user_role = st.session_state.current_user['role']
    is_admin = (user_role == 'admin')
    
    # Custom CSS for main app interface
    st.markdown("""
    <style>
        /* Reset for main app */
        .stApp {
            background: linear-gradient(135deg, #f8f9fc 0%, #ffffff 100%);
        }
        
        .block-container {
            padding: 2rem !important;
            max-width: 1200px !important;
            margin: 0 auto !important;
        }
        
        /* Modern Header */
        .modern-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem 3rem;
            border-radius: 24px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        }
        
        .modern-header h1 {
            font-size: 2rem;
            font-weight: 700;
            color: white;
            margin-bottom: 0.5rem;
        }
        
        .modern-header p {
            color: rgba(255,255,255,0.9);
            font-size: 0.9rem;
        }
        
        /* Navigation Bar */
        .nav-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 1.5rem;
            background: white;
            border-radius: 60px;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid #eef2f6;
        }
        
        .logo-area {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        
        .logo-text {
            font-size: 1.25rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .user-area {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .role-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 0.4rem 1.2rem;
            border-radius: 40px;
            color: white;
            font-size: 0.75rem;
            font-weight: 600;
        }
        
        .user-name-badge {
            background: #f0f2f5;
            padding: 0.4rem 1.2rem;
            border-radius: 40px;
            color: #1a1a2e;
            font-size: 0.8rem;
            font-weight: 500;
        }
        
        /* Modern Cards */
        .modern-card {
            background: white;
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1.25rem;
            border: 1px solid #eef2f6;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            transition: all 0.3s ease;
        }
        
        .modern-card:hover {
            box-shadow: 0 8px 30px rgba(102,126,234,0.08);
            transform: translateY(-2px);
        }
        
        .card-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 2px solid #f0f2f5;
            padding-bottom: 0.75rem;
        }
        
        /* Metric Cards */
        .metric-modern {
            background: white;
            border-radius: 16px;
            padding: 1rem;
            text-align: center;
            border: 1px solid #eef2f6;
        }
        
        .metric-value-modern {
            font-size: 1.75rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.25rem;
        }
        
        .metric-label-modern {
            font-size: 0.7rem;
            color: #64748b;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            background-color: white;
            padding: 0.5rem;
            border-radius: 60px;
            margin-bottom: 1.5rem;
            border: 1px solid #eef2f6;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 40px;
            padding: 0.5rem 1.5rem;
            font-size: 0.85rem;
            font-weight: 500;
            color: #64748b;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 40px;
            padding: 0.5rem 1.5rem;
            font-weight: 500;
        }
        
        /* Form inputs */
        .stTextInput > div > div > input, .stSelectbox > div > div, .stNumberInput > div > div > input {
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            padding: 0.6rem 1rem;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102,126,234,0.1);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    if is_admin:
        st.markdown("""
        <div class="modern-header">
            <h1>🛒 Admin Dashboard</h1>
            <p>Complete control over sales, operators, and rewards analytics</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="modern-header">
            <h1>🛒 Operator Dashboard</h1>
            <p>Record sales, track rewards, and view your daily performance</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation Bar
    st.markdown(f"""
    <div class="nav-bar">
        <div class="logo-area">
            <span style="font-size: 1.5rem;">🛒</span>
            <span class="logo-text">Tengai</span>
        </div>
        <div class="user-area">
            <span class="role-badge">{user_role.upper()}</span>
            <span class="user-name-badge">👋 {user_name}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    tab1, tab2 = st.tabs(["📝 Record Sale", "📊 My Sales Today"])
    
    # TAB 1: Record Sale
    with tab1:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📋 New Purchase</div>', unsafe_allow_html=True)
            
            with st.form(key="sales_form", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    customer_name = st.text_input("Customer Name *", placeholder="Enter full name")
                with col_b:
                    customer_email = st.text_input("Email Address", placeholder="customer@example.com")
                
                col_c, col_d = st.columns(2)
                with col_c:
                    customer_id = st.text_input("SPAR Rewards ID", placeholder="Optional")
                with col_d:
                    phone = st.text_input("Phone Number", placeholder="Optional")
                
                st.markdown("---")
                st.markdown("#### 🛍️ Purchase Details")
                
                col_e, col_f = st.columns(2)
                with col_e:
                    product = st.selectbox("Product Category", [
                        "Fresh Produce", "Meat and Poultry", "Dairy", 
                        "Bakery", "Beverages", "Household", "Personal Care"
                    ])
                with col_f:
                    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                
                col_g, col_h = st.columns(2)
                with col_g:
                    unit_price = st.number_input("Unit Price (USD)", min_value=0.01, value=49.99, step=0.01, format="%.2f")
                with col_h:
                    total_sales = quantity * unit_price
                    st.metric("Total Amount", f"${total_sales:,.2f}")
                
                rewards_earned = total_sales * 0.02
                st.info(f"⭐ Rewards Points Earned: {rewards_earned:.0f} (2% of purchase)")
                
                submitted = st.form_submit_button("💾 Record Sale", use_container_width=True)
                
                if submitted and customer_name:
                    now = datetime.now()
                    sale_id = generate_sale_id()
                    
                    data = {
                        'sale_id': sale_id,
                        'customer_name': customer_name,
                        'customer_email': customer_email,
                        'customer_id': customer_id if customer_id else None,
                        'phone': phone if phone else None,
                        'product_category': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_sales': total_sales,
                        'rewards_earned': rewards_earned,
                        'sale_date': now.strftime('%Y-%m-%d'),
                        'sale_month': now.strftime('%b').upper(),
                        'sale_year': now.year,
                        'sale_time': now.strftime('%H:%M:%S'),
                        'timestamp_utc': now.isoformat(),
                        'recorded_by': user_name,
                        'etl_processed': 0,
                        'etl_processed_at': None
                    }
                    
                    success, message = send_to_webhook(data)
                    send_admin_notification(customer_name, sale_id, product, quantity, total_sales, rewards_earned, customer_email)
                    st.session_state.sales_history.insert(0, data)
                    
                    if success:
                        st.success(f"✅ Sale recorded! ID: {sale_id}")
                        st.balloons()
                    else:
                        st.warning(f"⚠️ {message}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📊 Today\'s Stats</div>', unsafe_allow_html=True)
            
            if check_connection():
                st.success("✅ ETL Connected")
                today_sales = get_sales_from_db(operator_name=user_name, date_filter='today')
                if today_sales:
                    df_today = pd.DataFrame(today_sales)
                    total_revenue = df_today['total_sales'].sum() if 'total_sales' in df_today.columns else 0
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">${total_revenue:,.2f}</div>
                        <div class="metric-label-modern">Today's Revenue</div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">{len(df_today)}</div>
                        <div class="metric-label-modern">Transactions</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No sales recorded yet today")
            else:
                st.warning("⚠️ ETL Offline - Tunnel may be down")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: My Sales Today
    with tab2:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-header">📊 My Sales Today - {user_name}</div>', unsafe_allow_html=True)
        
        if check_connection():
            today_sales = get_sales_from_db(operator_name=user_name, date_filter='today')
            
            if today_sales:
                df = pd.DataFrame(today_sales)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">{len(df)}</div>
                        <div class="metric-label-modern">Transactions</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    total_revenue = df['total_sales'].sum() if 'total_sales' in df.columns else 0
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">${total_revenue:,.2f}</div>
                        <div class="metric-label-modern">Revenue</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    avg_sale = df['total_sales'].mean() if 'total_sales' in df.columns else 0
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">${avg_sale:.2f}</div>
                        <div class="metric-label-modern">Average Sale</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    customers = df['customer_name'].nunique() if 'customer_name' in df.columns else 0
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">{customers}</div>
                        <div class="metric-label-modern">Customers Served</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("#### 📋 Your Sales Today")
                display_cols = ['sale_id', 'customer_name', 'product_category', 'quantity', 'total_sales', 'sale_time']
                available_cols = [c for c in display_cols if c in df.columns]
                if available_cols:
                    st.dataframe(df[available_cols], use_container_width=True, height=400)
            else:
                st.info("No sales recorded today. Start selling! 🛒")
        else:
            st.warning("⚠️ Cannot connect to ETL server")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# ADMIN VIEW
# ============================================
def admin_view():
    user_name = st.session_state.current_user['name']
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Record Sale", "📊 Today's Sales", "📈 Sales Reports", "🏆 Rewards Analysis", "⚙️ Admin Panel"
    ])
    
    # TAB 1: Record Sale
    with tab1:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📋 New Purchase</div>', unsafe_allow_html=True)
            
            with st.form(key="sales_form_admin", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    customer_name = st.text_input("Customer Name *", placeholder="Enter full name")
                with col_b:
                    customer_email = st.text_input("Email Address", placeholder="customer@example.com")
                
                col_c, col_d = st.columns(2)
                with col_c:
                    customer_id = st.text_input("SPAR Rewards ID", placeholder="Optional")
                with col_d:
                    phone = st.text_input("Phone Number", placeholder="Optional")
                
                st.markdown("---")
                st.markdown("#### 🛍️ Purchase Details")
                
                col_e, col_f = st.columns(2)
                with col_e:
                    product = st.selectbox("Product Category", [
                        "Fresh Produce", "Meat and Poultry", "Dairy", 
                        "Bakery", "Beverages", "Household", "Personal Care"
                    ])
                with col_f:
                    quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                
                col_g, col_h = st.columns(2)
                with col_g:
                    unit_price = st.number_input("Unit Price (USD)", min_value=0.01, value=49.99, step=0.01, format="%.2f")
                with col_h:
                    total_sales = quantity * unit_price
                    st.metric("Total Amount", f"${total_sales:,.2f}")
                
                rewards_earned = total_sales * 0.02
                st.info(f"⭐ Rewards Points Earned: {rewards_earned:.0f} (2% of purchase)")
                
                submitted = st.form_submit_button("💾 Record Sale", use_container_width=True)
                
                if submitted and customer_name:
                    now = datetime.now()
                    sale_id = generate_sale_id()
                    
                    data = {
                        'sale_id': sale_id,
                        'customer_name': customer_name,
                        'customer_email': customer_email,
                        'customer_id': customer_id if customer_id else None,
                        'phone': phone if phone else None,
                        'product_category': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_sales': total_sales,
                        'rewards_earned': rewards_earned,
                        'sale_date': now.strftime('%Y-%m-%d'),
                        'sale_month': now.strftime('%b').upper(),
                        'sale_year': now.year,
                        'sale_time': now.strftime('%H:%M:%S'),
                        'timestamp_utc': now.isoformat(),
                        'recorded_by': user_name,
                        'etl_processed': 0,
                        'etl_processed_at': None
                    }
                    
                    success, message = send_to_webhook(data)
                    send_admin_notification(customer_name, sale_id, product, quantity, total_sales, rewards_earned, customer_email)
                    
                    if success:
                        st.success(f"✅ Sale recorded! ID: {sale_id}")
                        st.balloons()
                    else:
                        st.warning(f"⚠️ {message}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📊 System Status</div>', unsafe_allow_html=True)
            
            if check_connection():
                st.success("✅ ETL Connected")
                st.info("📤 Data is being sent to SQL Server")
            else:
                st.warning("⚠️ ETL Offline - Tunnel may be down")
                st.info("💡 Update your WEBHOOK_URL in Settings → Secrets")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: Today's All Sales
    with tab2:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📊 Today\'s All Sales (All Operators)</div>', unsafe_allow_html=True)
        
        if check_connection():
            today_sales = get_sales_from_db(date_filter='today')
            
            if today_sales:
                df = pd.DataFrame(today_sales)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">{len(df)}</div>
                        <div class="metric-label-modern">Transactions</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    total_revenue = df['total_sales'].sum() if 'total_sales' in df.columns else 0
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">${total_revenue:,.2f}</div>
                        <div class="metric-label-modern">Revenue</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    avg_sale = df['total_sales'].mean() if 'total_sales' in df.columns else 0
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">${avg_sale:.2f}</div>
                        <div class="metric-label-modern">Average Sale</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    operators = df['recorded_by'].nunique() if 'recorded_by' in df.columns else 0
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">{operators}</div>
                        <div class="metric-label-modern">Active Operators</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("#### 📋 Today's Sales Details")
                display_cols = ['sale_id', 'recorded_by', 'customer_name', 'product_category', 'quantity', 'total_sales', 'sale_time']
                available_cols = [c for c in display_cols if c in df.columns]
                if available_cols:
                    st.dataframe(df[available_cols], use_container_width=True, height=400)
                
                if 'recorded_by' in df.columns and 'total_sales' in df.columns:
                    st.markdown("#### 👥 Operator Performance Today")
                    operator_today = df.groupby('recorded_by').agg({
                        'sale_id': 'count',
                        'total_sales': 'sum'
                    }).rename(columns={'sale_id': 'Transactions', 'total_sales': 'Revenue'}).reset_index()
                    operator_today['Revenue'] = operator_today['Revenue'].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(operator_today, use_container_width=True)
            else:
                st.info("No sales recorded today")
        else:
            st.warning("⚠️ ETL Server not connected")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: Sales Reports
    with tab3:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📈 Sales Reports & Analytics</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        if check_connection():
            sales_data = get_sales_from_db(start_date=start_date, end_date=end_date)
            
            if sales_data:
                df = pd.DataFrame(sales_data)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    total_revenue = df['total_sales'].sum() if 'total_sales' in df.columns else 0
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">${total_revenue:,.2f}</div>
                        <div class="metric-label-modern">Total Sales</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">{len(df)}</div>
                        <div class="metric-label-modern">Transactions</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col3:
                    customers = df['customer_name'].nunique() if 'customer_name' in df.columns else 0
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">{customers}</div>
                        <div class="metric-label-modern">Unique Customers</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col4:
                    avg_sale = df['total_sales'].mean() if 'total_sales' in df.columns else 0
                    st.markdown(f"""
                    <div class="metric-modern">
                        <div class="metric-value-modern">${avg_sale:.2f}</div>
                        <div class="metric-label-modern">Avg Transaction</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                if 'sale_date' in df.columns and 'total_sales' in df.columns:
                    st.markdown("#### 📅 Daily Sales Trend")
                    df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
                    daily_sales = df.groupby('sale_date')['total_sales'].sum().reset_index()
                    fig = px.line(daily_sales, x='sale_date', y='total_sales', 
                                  title="Sales Over Time", markers=True,
                                  color_discrete_sequence=['#667eea'])
                    fig.update_layout(height=400, plot_bgcolor='white', paper_bgcolor='white')
                    st.plotly_chart(fig, use_container_width=True)
                
                if 'recorded_by' in df.columns:
                    st.markdown("#### 👥 Operator Performance")
                    operator_perf = df.groupby('recorded_by').agg({
                        'sale_id': 'count',
                        'total_sales': 'sum'
                    }).rename(columns={'sale_id': 'Transactions', 'total_sales': 'Revenue'}).reset_index()
                    operator_perf['Revenue'] = operator_perf['Revenue'].apply(lambda x: f"${x:,.2f}")
                    st.dataframe(operator_perf, use_container_width=True)
                
                st.markdown("---")
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Full Report (CSV)",
                    data=csv,
                    file_name=f"spar_sales_report_{start_date}_to_{end_date}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.info(f"No sales found between {start_date} and {end_date}")
        else:
            st.warning("⚠️ Cannot connect to ETL server")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 4: Rewards Analysis
    with tab4:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🏆 Rewards Intelligence Hub</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'], key="rewards_upload")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            df = clean_rewards_data(df)
            
            if not df.empty:
                st.success(f"✅ Loaded {len(df)} transactions from {df['member_number'].nunique()} unique customers")
                
                rfm = calculate_rfm(df)
                rfm = segment_customers(rfm)
                rfm = calculate_clv(rfm)
                rfm = calculate_churn_probability(rfm)
                rfm = generate_actions(rfm)
                rfm = rfm.reset_index()
                
                seg_counts = rfm['segment'].value_counts().reset_index()
                seg_counts.columns = ['Segment', 'Count']
                fig = px.pie(seg_counts, values='Count', names='Segment', 
                             color_discrete_sequence=['#667eea', '#f59e0b', '#ef4444', '#10b981', '#8b5cf6'],
                             hole=0.3)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("No valid data found")
        else:
            st.info("📂 Upload a CSV file with columns: member_number, redemption_date, basket_value")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 5: Admin Panel
    with tab5:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">👑 Admin Control Panel</div>', unsafe_allow_html=True)
        
        st.markdown("#### ➕ Create New Operator Account")
        
        with st.form("create_operator_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name *", placeholder="Operator's full name")
                new_username = st.text_input("Username *", placeholder="operator_username")
            with col2:
                new_email = st.text_input("Email *", placeholder="operator@store.com")
                new_password = st.text_input("Password *", type="password", placeholder="Min 6 characters")
            
            submitted = st.form_submit_button("👤 Create Operator", use_container_width=True)
            
            if submitted:
                if not all([new_name, new_username, new_email, new_password]):
                    st.error("Please fill all fields")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, message = register_user(new_name, new_username, new_email, new_password, role="user")
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
        
        st.markdown("---")
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
        st.markdown("#### 📊 System Status")
        
        if check_connection():
            st.success("✅ ETL Server Connected")
        else:
            st.error("❌ ETL Server Offline")
        
        st.markdown("---")
        st.markdown("#### 🔧 Current Configuration")
        st.code(f"WEBHOOK_URL = {WEBHOOK_URL}", language="python")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN
# ============================================
if st.session_state.logged_in:
    main_app_interface()
else:
    login_screen()
