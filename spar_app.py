import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import hashlib
import time

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
# WEBHOOK URL
# ============================================
WEBHOOK_URL = "https://kitchen-council-identification-technological.trycloudflare.com/webhook"

# Configure page
st.set_page_config(
    page_title="Tengai - SPAR Sales & Rewards System",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SPAR Brand Colours (exactly from image)
SPAR_RED = "#E3000F"
SPAR_GREEN = "#007A3D"
SPAR_DARK_RED = "#C4000D"
SPAR_GRADIENT = "linear-gradient(135deg, #E3000F 0%, #007A3D 100%)"

# Modern colours
WHITE = "#FFFFFF"
BORDER = "#E5E7EB"
LIGHT_GREY = "#F9FAFB"
DARK_GREY = "#6B7280"

# Custom CSS - CENTERED EVERYTHING with SPAR colors
st.markdown(f"""
    <style>
    /* Main container - center everything */
    .stApp {{
        background: linear-gradient(135deg, #F0F2F6 0%, #FFFFFF 100%);
    }}
    
    /* Center main content */
    .main-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    /* Centered header bar */
    .app-header {{
        background: {SPAR_GRADIENT};
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
    
    /* Center the login box */
    .login-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }}
    
    .login-box {{
        background: {WHITE};
        border-radius: 32px;
        padding: 2rem;
        max-width: 450px;
        width: 100%;
        margin: 0 auto;
        box-shadow: 0 20px 40px rgba(0,0,0,0.08);
        border: 1px solid {BORDER};
        text-align: center;
    }}
    
    .app-name {{
        font-size: 2.2rem;
        font-weight: 800;
        color: {SPAR_RED};
        text-align: center;
        margin-bottom: 0.5rem;
    }}
    
    .subtitle {{
        color: {DARK_GREY};
        font-size: 0.8rem;
        text-align: center;
        margin-bottom: 0.8rem;
    }}
    
    .version-badge {{
        text-align: center;
        margin-bottom: 1.5rem;
    }}
    
    .badge {{
        background: {LIGHT_GREY};
        padding: 0.25rem 0.8rem;
        border-radius: 30px;
        font-size: 0.7rem;
        color: {DARK_GREY};
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }}
    
    .dot {{
        width: 5px;
        height: 5px;
        background-color: {SPAR_GREEN};
        border-radius: 50%;
        display: inline-block;
    }}
    
    /* Center buttons */
    .stButton > button {{
        background-color: {SPAR_RED};
        color: white;
        border: none;
        padding: 0.6rem;
        font-weight: 600;
        border-radius: 40px;
        width: 100%;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {SPAR_DARK_RED};
        transform: translateY(-1px);
    }}
    
    /* Center tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background-color: {LIGHT_GREY};
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
        white-space: nowrap;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {SPAR_RED};
        color: white;
    }}
    
    /* Center input fields */
    .stTextInput > div > div > input {{
        border-radius: 16px;
        border: 1px solid {BORDER};
        padding: 0.7rem 1rem;
        font-size: 0.85rem;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {SPAR_RED};
        box-shadow: 0 0 0 3px rgba(227, 0, 15, 0.1);
    }}
    
    /* Center selectbox */
    .stSelectbox > div > div {{
        border-radius: 16px;
    }}
    
    /* Card styling with left border accent */
    .content-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 24px;
        margin-bottom: 1rem;
        border: 1px solid {BORDER};
        border-left: 4px solid {SPAR_RED};
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }}
    
    /* Center metrics */
    .stMetric {{
        text-align: center;
    }}
    
    /* User info right aligned but overall centered layout */
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
    
    /* Hide default menu */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Center column content */
    .stColumn {{
        text-align: center;
    }}
    
    /* Center expander */
    .streamlit-expanderHeader {{
        text-align: center;
    }}
    
    /* Center dataframes */
    .stDataFrame {{
        text-align: center;
    }}
    
    hr {{
        margin: 1rem 0;
        border-color: {BORDER};
    }}
    
    .section-title {{
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: {SPAR_RED};
        text-align: center;
    }}
    
    .metric-value {{
        color: {SPAR_RED};
        font-size: 1.8rem;
        font-weight: 700;
    }}
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
if 'offline_queue' not in st.session_state:
    st.session_state.offline_queue = []

# ============================================
# HELPER FUNCTIONS
# ============================================

def generate_sale_id():
    return f"SPAR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def send_to_webhook(data):
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if response.status_code == 200:
            return True, "Data sent to ETL"
        return False, f"Server error: {response.status_code}"
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
        <body>
            <h2 style="color:#E3000F;">New SPAR Sale Recorded!</h2>
            <p><strong>Sale ID:</strong> {sale_id}</p>
            <p><strong>Customer:</strong> {customer_name}</p>
            <p><strong>Product:</strong> {product}</p>
            <p><strong>Quantity:</strong> {quantity}</p>
            <p><strong>Total:</strong> ${total_sales:,.2f}</p>
            <p><strong>Rewards:</strong> {rewards_earned:.0f} points</p>
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
    except:
        return False

def check_connection():
    try:
        response = requests.get(WEBHOOK_URL.replace('/webhook', '/health'), timeout=5)
        return response.status_code == 200
    except:
        return False

# ============================================
# LOGIN/REGISTER SCREEN (CENTERED)
# ============================================

def login_register_screen():
    # Centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.markdown('<div class="app-name">Tengai</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Sign in to continue.</div>', unsafe_allow_html=True)
        st.markdown("""
            <div class="version-badge">
                <div class="badge"><span class="dot"></span> Version 3.3.0 • Production</div>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        
        with tab1:
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username / Email", placeholder="Enter your username or email")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                
                if submitted:
                    if username and password:
                        success, message = login_user(username, password)
                        if success:
                            st.success(message)
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please enter username/email and password")
        
        with tab2:
            with st.form("register_form", clear_on_submit=False):
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
                            st.session_state.active_tab = "login"
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(message)
        
        st.markdown('<div style="text-align: center; margin-top: 1rem; font-size: 0.7rem; color: #9ca3af;"><i class="fas fa-lock"></i> Secure session • Mode Production</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN APP CONTENT (CENTERED HEADERS)
# ============================================

def main_app():
    # Centered Header
    st.markdown(f"""
    <div class="app-header">
        <h1>🛒 Tengai - SPAR Sales & Rewards System</h1>
        <p>Your trusted partner in retail excellence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User info row (centered with right alignment)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col3:
        st.markdown(f"""
        <div style="display: flex; justify-content: flex-end;">
            <div class="user-info">
                👋 {st.session_state.current_user['name']} ({st.session_state.current_user['role'].upper()})
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", key="signout_btn", use_container_width=False):
            logout_user()
            st.rerun()
    
    # Centered Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Record Sale", "🏆 Rewards Analysis", "📊 Dashboard", "⚙️ Settings"])
    
    # TAB 1: Record Sale
    with tab1:
        col_left, col_right = st.columns([2, 1], gap="large")
        
        with col_left:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="text-align: center; color: #E3000F;">📋 New Purchase</h3>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            
            sale_id = generate_sale_id()
            
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
                st.markdown('<p style="text-align: center; font-weight: 600;">🛍️ Purchase Details</p>', unsafe_allow_html=True)
                
                col_e, col_f = st.columns(2)
                with col_e:
                    product = st.selectbox("Product *", [
                        "Fresh Produce", "Meat & Poultry", "Dairy", 
                        "Bakery", "Beverages", "Household", "Personal Care"
                    ])
                
                with col_f:
                    quantity = st.number_input("Quantity *", min_value=1, value=1, step=1)
                
                col_g, col_h = st.columns(2)
                with col_g:
                    unit_price = st.number_input("Unit Price (USD) *", min_value=0.01, value=49.99, step=0.01, format="%.2f")
                with col_h:
                    total_sales = quantity * unit_price
                    st.markdown(f"""
                    <div style="background:{LIGHT_GREY}; padding:0.8rem; border-radius:20px; text-align:center; margin-top:1.8rem;">
                        💰 <strong>Total:</strong> <span style="color:{SPAR_RED}; font-size:1.2rem;">${total_sales:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                rewards_earned = total_sales * 0.02
                st.info(f"⭐ Rewards Points: {rewards_earned:.0f} (2% of purchase)")
                
                send_receipt = st.checkbox("📧 Send receipt to customer", value=True)
                
                submitted = st.form_submit_button("💾 Record Sale", use_container_width=True)
                
                if submitted:
                    if not customer_name or not product:
                        st.error("❌ Please fill all required fields")
                    else:
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
                        
                        success, _ = send_to_webhook(data)
                        send_admin_notification(customer_name, sale_id, product, quantity, total_sales, rewards_earned, customer_email)
                        
                        if success:
                            st.success(f"✅ Sale recorded! ID: {sale_id}")
                            if send_receipt and customer_email:
                                st.info(f"📧 Receipt sent to {customer_email}")
                            st.balloons()
                        else:
                            st.warning(f"⚠️ Sale recorded but ETL offline")
                        
                        st.session_state.sales_history.insert(0, data)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="text-align: center;">📊 Live Status</h3>', unsafe_allow_html=True)
            st.markdown("<hr>", unsafe_allow_html=True)
            
            if check_connection():
                st.success("✅ ETL Connected")
            else:
                st.warning("⚠️ ETL Offline")
            
            if st.session_state.sales_history:
                df = pd.DataFrame(st.session_state.sales_history)
                st.metric("Session Sales", f"${df['total_sales'].sum():,.2f}")
                st.metric("Transactions", len(df))
                st.metric("Rewards Given", f"{df['rewards_earned'].sum():,.0f} pts")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: Rewards Analysis
    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; color: #E3000F;">🏆 Rewards Analysis</h2>', unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload CSV for analysis", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} records")
            st.dataframe(df.head(), use_container_width=True)
            
            # Show basic stats
            if 'total_sales' in df.columns or 'amount' in df.columns:
                sales_col = 'total_sales' if 'total_sales' in df.columns else 'amount'
                st.metric("Total Sales from CSV", f"${df[sales_col].sum():,.2f}")
        else:
            st.info("📂 Upload a CSV file to analyze rewards and customer insights")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: Dashboard
    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; color: #E3000F;">📊 Sales Dashboard</h2>', unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        if st.session_state.sales_history:
            df = pd.DataFrame(st.session_state.sales_history)
            
            # Metrics row
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sales", f"${df['total_sales'].sum():,.2f}")
            with col2:
                st.metric("Transactions", len(df))
            with col3:
                st.metric("Rewards Given", f"{df['rewards_earned'].sum():,.0f} pts")
            
            st.markdown("---")
            st.markdown('<p style="text-align: center; font-weight: 600;">📋 Recent Transactions</p>', unsafe_allow_html=True)
            st.dataframe(df[['sale_id', 'customer_name', 'product', 'total_sales']].head(10), use_container_width=True)
            
            csv = df.to_csv(index=False)
            st.download_button("📥 Download Data as CSV", csv, f"tengai_sales_{datetime.now().strftime('%Y%m%d')}.csv", use_container_width=True)
        else:
            st.info("📭 No sales recorded yet. Start by recording a sale!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 4: Settings
    with tab4:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<h2 style="text-align: center; color: #E3000F;">⚙️ Settings</h2>', unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)
        
        st.markdown('<h3 style="text-align: center;">👤 My Profile</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.write(f"**Name:** {st.session_state.current_user['name']}")
            st.write(f"**Email:** {st.session_state.current_user['email']}")
            st.write(f"**Username:** {st.session_state.current_user['username']}")
            st.write(f"**Role:** {st.session_state.current_user['role'].capitalize()}")
        
        if st.session_state.current_user['role'] == 'admin':
            st.divider()
            st.markdown('<h3 style="text-align: center;">👑 Admin Panel</h3>', unsafe_allow_html=True)
            
            with st.expander("📋 Registered Users"):
                users = get_all_users()
                if users:
                    users_list = [{'Name': u['name'], 'Email': e, 'Username': u['username'], 'Role': u['role']} 
                                  for e, u in users.items()]
                    st.dataframe(pd.DataFrame(users_list), use_container_width=True)
            
            with st.expander("📁 Export System Data"):
                users = get_all_users()
                if users:
                    users_df = pd.DataFrame([{'Name': u['name'], 'Email': e, 'Username': u['username'], 'Role': u['role']} 
                                            for e, u in users.items()])
                    csv = users_df.to_csv(index=False)
                    st.download_button("Download Users CSV", csv, "tengai_users.csv", use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN
# ============================================

if st.session_state.logged_in:
    main_app()
else:
    login_register_screen()
