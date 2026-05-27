import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re
import hashlib
import time
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# ============================================
# APP CONFIGURATION
# ============================================
APP_NAME = "Tengai"
APP_VERSION = "3.3.0"
DEPLOYMENT_MODE = "production"

# ============================================
# EMAIL CONFIGURATION
# ============================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "gomoraefesto97@gmail.com"
SENDER_PASSWORD = "picz cijg kgbw zoup"
ADMIN_EMAIL = "gomoraefesto97@gmail.com"

# ============================================
# WEBHOOK URL (Updated with your new tunnel)
# ============================================
WEBHOOK_URL = "https://partially-casino-docs-bunny.trycloudflare.com"

# ============================================
# SPAR BRAND COLORS
# ============================================
SPAR_RED = "#E3000F"
SPAR_GREEN = "#007A3D"
SPAR_DARK_RED = "#C4000D"
SPAR_LIGHT_GREEN = "#A8D46B"
SPAR_GRAY = "#f6f7fb"

# Configure page
st.set_page_config(
    page_title="Tengai - SPAR Sales & Rewards System",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with centered headers
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    .stApp {{
        background: linear-gradient(135deg, #F0F2F6 0%, #FFFFFF 100%);
    }}
    
    /* Centered Header */
    .app-header {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        padding: 1.5rem 2rem;
        border-radius: 28px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
    }}
    
    .app-header h1 {{
        margin: 0;
        font-size: 1.8rem;
        font-weight: 800;
        color: white;
        text-align: center;
    }}
    
    .app-header p {{
        margin: 0.3rem 0 0 0;
        opacity: 0.9;
        font-size: 0.8rem;
        color: white;
        text-align: center;
    }}
    
    /* Centered Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background-color: {SPAR_GRAY};
        padding: 0.4rem;
        border-radius: 60px;
        justify-content: center;
        display: flex;
        margin-bottom: 1.5rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 40px;
        padding: 0.5rem 1.5rem;
        font-size: 0.85rem;
        font-weight: 600;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {SPAR_RED};
        color: white;
    }}
    
    /* Cards */
    .content-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 24px;
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
        border-left: 4px solid {SPAR_RED};
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, white 0%, {SPAR_GRAY} 100%);
        padding: 1.2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
        border-top: 3px solid {SPAR_RED};
    }}
    
    .big-number {{
        font-weight: 800;
        font-size: 28px;
        color: {SPAR_RED};
        margin-bottom: 5px;
    }}
    
    /* Login box */
    .login-box {{
        background: white;
        border-radius: 32px;
        padding: 2rem;
        max-width: 450px;
        margin: 0 auto;
        box-shadow: 0 20px 40px rgba(0,0,0,0.08);
        border: 1px solid #E5E7EB;
        text-align: center;
    }}
    
    .app-name {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {SPAR_RED};
        text-align: center;
    }}
    
    .user-info {{
        background: {SPAR_RED};
        padding: 0.3rem 1rem;
        border-radius: 40px;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.75rem;
        color: white;
    }}
    
    .btn-primary > button {{
        background-color: {SPAR_RED};
        color: white;
        border: none;
        border-radius: 40px;
        font-weight: 600;
    }}
    
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

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
        'created_at': datetime.now().isoformat()
    }
    with open(get_users_file(), 'w') as f:
        json.dump(users, f, indent=2)
    return True

def init_default_admin():
    users = get_all_users()
    if len(users) == 0:
        save_user("admin@tengai.com", "Administrator", "admin", hash_password("Admin@123"), "admin")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def register_user(name, username, email, password):
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
    role = "admin" if len(users) == 0 else "user"
    password_hash = hash_password(password)
    save_user(email, name, username, password_hash, role)
    return True, f"Registration successful! You are the {role}."

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
    st.session_state.active_tab = "login"

# Initialize
init_default_admin()

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "login"
if 'sales_history' not in st.session_state:
    st.session_state.sales_history = []
if 'rewards_df' not in st.session_state:
    st.session_state.rewards_df = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ============================================
# REWARDS ANALYSIS FUNCTIONS (from your code)
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
    rfm['segment'] = '📊 Other'
    mask_active = (rfm['recency'] <= 30)
    rfm.loc[mask_active, 'segment'] = "⭐ Active"
    mask_warming = (rfm['recency'] > 30) & (rfm['recency'] <= 60)
    rfm.loc[mask_warming, 'segment'] = "⚠️ Warming"
    mask_at_risk = (rfm['recency'] > 60) & (rfm['recency'] <= 90)
    rfm.loc[mask_at_risk, 'segment'] = "⚠️ At Risk"
    mask_churned = (rfm['recency'] > 90)
    rfm.loc[mask_churned, 'segment'] = "💔 Churned"
    mask_one_time = (rfm['frequency'] == 1) & (rfm['segment'] == '📊 Other')
    rfm.loc[mask_one_time, 'segment'] = "🆕 One-Time"
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
        if row['segment'] == '⚠️ At Risk':
            actions.append("🚨 URGENT: Send 30% discount + personalized email")
            priorities.append("High")
        elif row['segment'] == '⚠️ Warming':
            actions.append("⚡ ACT NOW: Send 15% off + engagement email")
            priorities.append("High")
        elif row['segment'] == '💔 Churned':
            actions.append("🔄 Win-back campaign with special offer")
            priorities.append("High")
        elif row['segment'] == '🆕 One-Time':
            actions.append("🎁 Welcome back incentive + loyalty program invite")
            priorities.append("Medium")
        elif row['segment'] == '⭐ Active':
            actions.append("🎉 Thank you for shopping! Check out our latest offers")
            priorities.append("Low")
        else:
            actions.append("📈 Nurture engagement with regular content")
            priorities.append("Low")
    rfm['recommended_action'] = actions
    rfm['priority'] = priorities
    return rfm

def generate_alerts(rfm):
    alerts = []
    at_risk = len(rfm[rfm['segment'] == '⚠️ At Risk'])
    warming = len(rfm[rfm['segment'] == '⚠️ Warming'])
    if at_risk > 30:
        alerts.append(f"⚠️ WARNING: {at_risk} customers at risk + {warming} warming up! Immediate action recommended!")
    elif warming > 50:
        alerts.append(f"⚠️ HEADS UP: {warming} customers showing early warning signs")
    churned = len(rfm[rfm['segment'] == '💔 Churned'])
    if churned > 100:
        alerts.append(f"💔 ALERT: {churned} customers have churned. Re-engagement campaign needed!")
    return alerts

def safe_currency_format(value):
    try:
        if pd.isna(value) or value is None:
            return "$0"
        return f"${float(value):,.0f}"
    except:
        return "$0"

# ============================================
# HELPER FUNCTIONS - FIXED WEBHOOK
# ============================================
def generate_sale_id():
    return f"SPAR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def send_to_webhook(data):
    """Send sales data to local ETL via webhook"""
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
        msg['Subject'] = f"🛒 NEW SALE - {sale_id}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #E3000F;">New SPAR Sale Recorded!</h2>
            <p><strong>Sale ID:</strong> {sale_id}</p>
            <p><strong>Customer:</strong> {customer_name}</p>
            <p><strong>Email:</strong> {customer_email if customer_email else 'Not provided'}</p>
            <p><strong>Product:</strong> {product}</p>
            <p><strong>Quantity:</strong> {quantity}</p>
            <p><strong>Total:</strong> ${total_sales:,.2f}</p>
            <p><strong>Rewards:</strong> {rewards_earned:.0f} points</p>
            <p><strong>Recorded by:</strong> {st.session_state.current_user['name'] if st.session_state.current_user else 'Unknown'}</p>
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

def check_connection():
    try:
        response = requests.get(WEBHOOK_URL.replace('/webhook', '/health'), timeout=5)
        return response.status_code == 200
    except:
        return False

# ============================================
# LOGIN/REGISTER SCREEN
# ============================================
def login_register_screen():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="app-name">Tengai</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666;">SPAR Sales & Rewards System</p>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username / Email", placeholder="Enter your username or email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                if submitted and username and password:
                    success, message = login_user(username, password)
                    if success:
                        st.success(message)
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(message)
        
        with tab2:
            with st.form("register_form"):
                name = st.text_input("Full Name", placeholder="Enter your full name")
                username = st.text_input("Username", placeholder="Choose a username")
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="Min 6 characters")
                confirm = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Create Account", use_container_width=True)
                if submitted:
                    if not all([name, username, email, password]):
                        st.error("Please fill all fields")
                    elif password != confirm:
                        st.error("Passwords do not match")
                    else:
                        success, message = register_user(name, username, email, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN APP
# ============================================
def main_app():
    # Centered Header
    st.markdown(f"""
    <div class="app-header">
        <h1>🛒 Tengai - SPAR Sales & Rewards System</h1>
        <p>Sales tracking • Rewards intelligence • Customer retention</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User info row
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end;">
            <div class="user-info">
                👋 {st.session_state.current_user['name']} ({st.session_state.current_user['role'].upper()})
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", key="signout"):
            logout_user()
            st.rerun()
    
    # Main Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Record Sale", "🏆 Rewards Analysis", "📊 Customer Intelligence", "🎯 Action Center", "⚙️ Settings"])
    
    # TAB 1: Record Sale
    with tab1:
        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("### 📋 New Purchase")
            
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
                    product = st.selectbox("Product", [
                        "Fresh Produce", "Meat & Poultry", "Dairy", 
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
                    sale_id = generate_sale_id()
                    data = {
                        'sale_id': sale_id,
                        'customer_name': customer_name,
                        'customer_email': customer_email,
                        'customer_id': customer_id,
                        'phone': phone,
                        'product': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_sales': total_sales,
                        'rewards_earned': rewards_earned,
                        'timestamp': datetime.now().isoformat(),
                        'recorded_by': st.session_state.current_user['name']
                    }
                    
                    # Send to webhook
                    success, message = send_to_webhook(data)
                    
                    # Send email notification
                    send_admin_notification(customer_name, sale_id, product, quantity, total_sales, rewards_earned, customer_email)
                    
                    # Store in session
                    st.session_state.sales_history.insert(0, data)
                    
                    if success:
                        st.success(f"✅ Sale recorded! ID: {sale_id}")
                        st.info(f"📤 {message}")
                        st.balloons()
                    else:
                        st.warning(f"⚠️ Sale recorded but not sent to ETL: {message}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Session Status")
            
            # Check ETL connection
            if check_connection():
                st.success("✅ ETL Connected")
            else:
                st.warning("⚠️ ETL Offline - Data will be saved locally")
            
            if st.session_state.sales_history:
                df = pd.DataFrame(st.session_state.sales_history)
                st.metric("Session Sales", f"${df['total_sales'].sum():,.2f}")
                st.metric("Transactions", len(df))
                st.metric("Rewards Given", f"{df['rewards_earned'].sum():,.0f} pts")
            else:
                st.info("No sales recorded yet")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: Rewards Analysis (Upload CSV)
    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 🏆 Rewards Intelligence Hub")
        st.markdown("Upload your customer transaction data to unlock powerful insights")
        
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'], key="rewards_upload")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            df = clean_rewards_data(df)
            
            if not df.empty:
                st.session_state.rewards_df = df
                st.success(f"✅ Loaded {len(df)} transactions from {df['member_number'].nunique()} unique customers")
                
                # Quick metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Revenue", safe_currency_format(df['basket_value'].sum()))
                with col2:
                    st.metric("Total Transactions", f"{len(df):,}")
                with col3:
                    st.metric("Unique Customers", f"{df['member_number'].nunique():,}")
                with col4:
                    st.metric("Avg Basket", safe_currency_format(df['basket_value'].mean()))
                
                # Process RFM and segments
                rfm = calculate_rfm(df)
                rfm = segment_customers(rfm)
                rfm = calculate_clv(rfm)
                rfm = calculate_churn_probability(rfm)
                rfm = generate_actions(rfm)
                rfm = rfm.reset_index()
                
                # Store in session for other tabs
                st.session_state.rfm_data = rfm
                st.session_state.raw_data = df
                
                # Segment Distribution Chart
                st.markdown("---")
                st.markdown("#### 📊 Customer Segment Distribution")
                
                seg_counts = rfm['segment'].value_counts().reset_index()
                seg_counts.columns = ['Segment', 'Count']
                fig = px.pie(seg_counts, values='Count', names='Segment', 
                             color_discrete_sequence=[SPAR_GREEN, SPAR_RED, '#FFA07A', '#D3D3D3', '#90EE90'],
                             hole=0.3)
                fig.update_layout(height=400, title="Customer Segments")
                st.plotly_chart(fig, use_container_width=True)
                
                # CLV Distribution
                st.markdown("#### 💰 Customer Lifetime Value Distribution")
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.histogram(rfm, x='clv', nbins=30, title="CLV Distribution",
                                      color_discrete_sequence=[SPAR_GREEN])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                with col2:
                    clv_by_segment = rfm.groupby('segment')['clv'].mean().reset_index()
                    fig = px.bar(clv_by_segment, x='segment', y='clv', title="Avg CLV by Segment",
                                color_discrete_sequence=[SPAR_RED])
                    fig.update_layout(height=350)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Age Group Analysis
                if 'age_group' in rfm.columns:
                    st.markdown("#### 👥 Age Group Analysis")
                    age_counts = rfm['age_group'].value_counts().reset_index()
                    age_counts.columns = ['Age Group', 'Count']
                    fig = px.bar(age_counts, x='Age Group', y='Count', title="Customers by Age",
                                color_discrete_sequence=[SPAR_GREEN])
                    st.plotly_chart(fig, use_container_width=True)
                
                # Churn Risk
                st.markdown("#### 📉 Churn Risk Analysis")
                churn_dist = rfm['churn_risk'].value_counts().reset_index()
                churn_dist.columns = ['Risk Level', 'Count']
                fig = px.bar(churn_dist, x='Risk Level', y='Count', title="Churn Risk Distribution",
                            color='Risk Level',
                            color_discrete_map={'Very Low': SPAR_GREEN, 'Low': '#90EE90', 
                                               'Medium': '#FFA500', 'High': SPAR_RED})
                st.plotly_chart(fig, use_container_width=True)
                
                # Export buttons
                st.markdown("---")
                col1, col2 = st.columns(2)
                with col1:
                    csv = rfm[['member_number', 'segment', 'clv_segment', 'churn_risk', 'recency', 'frequency', 'monetary', 'priority']].to_csv(index=False)
                    st.download_button("📥 Download Full Analysis", csv, "rewards_analysis.csv", use_container_width=True)
                with col2:
                    high_priority = rfm[rfm['priority'] == 'High'][['member_number', 'monetary', 'segment', 'recency']]
                    if not high_priority.empty:
                        high_csv = high_priority.to_csv(index=False)
                        st.download_button("🚨 Download High Priority List", high_csv, "high_priority_customers.csv", use_container_width=True)
                
            else:
                st.error("No valid data found. Please check your file format.")
        else:
            st.info("📂 Please upload a CSV file with columns: Member Number, Redemption Date, Basket Value")
            with st.expander("📖 View sample data format"):
                sample_df = pd.DataFrame({
                    'Member Number': ['M001234', 'M001234', 'M005678'],
                    'Redemption Date': ['2026-04-01', '2026-03-15', '2026-04-05'],
                    'Basket Value': [45.50, 32.00, 89.99],
                    'Birthday': ['1990-05-15', '1990-05-15', '1985-12-20']
                })
                st.dataframe(sample_df)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: Customer Intelligence Dashboard
    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Customer Intelligence Dashboard")
        
        if hasattr(st.session_state, 'rfm_data') and st.session_state.rfm_data is not None:
            rfm = st.session_state.rfm_data
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Customers", f"{len(rfm):,}")
            with col2:
                st.metric("Avg CLV", safe_currency_format(rfm['clv'].mean()))
            with col3:
                active_rate = len(rfm[rfm['recency'] <= 30]) / len(rfm) * 100
                st.metric("Active Rate (30d)", f"{active_rate:.1f}%")
            with col4:
                retention_rate = len(rfm[rfm['frequency'] > 1]) / len(rfm) * 100
                st.metric("Retention Rate", f"{retention_rate:.1f}%")
            
            # Alerts
            alerts = generate_alerts(rfm)
            if alerts:
                st.markdown("#### 🚨 Alerts")
                for alert in alerts:
                    if "WARNING" in alert:
                        st.warning(alert)
                    elif "ALERT" in alert:
                        st.error(alert)
                    else:
                        st.info(alert)
            
            # Customer data table
            st.markdown("#### 📋 Customer Details")
            display_cols = ['member_number', 'segment', 'clv_segment', 'churn_risk', 
                           'recency', 'frequency', 'monetary', 'priority']
            display_df = rfm[display_cols].copy()
            display_df['monetary'] = display_df['monetary'].apply(lambda x: safe_currency_format(x))
            display_df['recency'] = display_df['recency'].apply(lambda x: f"{int(x)} days")
            st.dataframe(display_df, use_container_width=True, height=400)
            
        else:
            st.info("📂 Please upload a rewards CSV file in the 'Rewards Analysis' tab first to see customer intelligence.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 4: Action Center
    with tab4:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Action Center - Recommended Customer Outreach")
        
        if hasattr(st.session_state, 'rfm_data') and st.session_state.rfm_data is not None:
            rfm = st.session_state.rfm_data
            
            high_priority = rfm[rfm['priority'] == 'High'].head(15)
            medium_priority = rfm[rfm['priority'] == 'Medium'].head(10)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### 🔴 High Priority ({len(rfm[rfm['priority']=='High'])} customers)")
                for idx, row in high_priority.iterrows():
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_DARK_RED} 100%); 
                                padding: 12px; border-radius: 12px; margin-bottom: 10px; color: white;">
                        <strong>{row['recommended_action']}</strong><br>
                        👤 Member: {row['member_number']} | 💰 {safe_currency_format(row['monetary'])} | 
                        ⏰ {int(row['recency'])} days ago | {row['segment']}
                    </div>
                    """, unsafe_allow_html=True)
                if high_priority.empty:
                    st.info("No high priority actions")
            
            with col2:
                st.markdown(f"#### 🟡 Medium Priority ({len(rfm[rfm['priority']=='Medium'])} customers)")
                for idx, row in medium_priority.iterrows():
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {SPAR_GREEN} 0%, {SPAR_LIGHT_GREEN} 100%); 
                                padding: 12px; border-radius: 12px; margin-bottom: 10px; color: white;">
                        <strong>{row['recommended_action']}</strong><br>
                        👤 Member: {row['member_number']} | 💰 {safe_currency_format(row['monetary'])} | {row['segment']}
                    </div>
                    """, unsafe_allow_html=True)
                if medium_priority.empty:
                    st.info("No medium priority actions")
            
            # Export actions
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                action_export = rfm[rfm['priority'] == 'High'][['member_number', 'recommended_action', 'monetary', 'recency', 'segment']]
                if not action_export.empty:
                    csv = action_export.to_csv(index=False)
                    st.download_button("📥 Export High Priority Actions", csv, "high_priority_actions.csv", use_container_width=True)
        else:
            st.info("📂 Please upload a rewards CSV file in the 'Rewards Analysis' tab first to see recommended actions.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 5: Settings
    with tab5:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Settings")
        
        st.markdown("#### 👤 My Profile")
        st.write(f"**Name:** {st.session_state.current_user['name']}")
        st.write(f"**Email:** {st.session_state.current_user['email']}")
        st.write(f"**Username:** {st.session_state.current_user['username']}")
        st.write(f"**Role:** {st.session_state.current_user['role'].capitalize()}")
        
        if st.session_state.current_user['role'] == 'admin':
            st.divider()
            st.markdown("#### 👑 Admin Panel")
            users = get_all_users()
            if users:
                users_list = [{'Name': u['name'], 'Email': e, 'Username': u['username'], 'Role': u['role']} 
                              for e, u in users.items()]
                st.dataframe(pd.DataFrame(users_list), use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN
# ============================================
if st.session_state.logged_in:
    main_app()
else:
    login_register_screen()
