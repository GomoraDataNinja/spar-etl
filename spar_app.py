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
SENDER_EMAIL = "your_email@gmail.com"  # Update this
SENDER_PASSWORD = "your_app_password"  # Update this
ADMIN_EMAIL = "gomoraefesto97@gmail.com"

# ============================================
# WEBHOOK URL (Update with your tunnel)
# ============================================
WEBHOOK_URL = "https://assessed-triumph-accessed-nam.trycloudflare.com/webhook"

# Configure page
st.set_page_config(
    page_title="Tengai - SPAR Sales & Rewards System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SPAR Brand Colours
SPAR_RED = "#E3000F"
SPAR_GREEN = "#007A3D"
SPAR_DARK_RED = "#C4000D"
SPAR_DARK_GREEN = "#005C2E"

# Modern colours
GOOGLE_WHITE = "#FFFFFF"
GOOGLE_BORDER = "#DADCE0"
GOOGLE_LIGHT_GREY = "#F8F9FA"
GOOGLE_DARK_GREY = "#5F6368"

# Custom CSS - No blue background outside
st.markdown(f"""
    <style>
    /* Main app background - clean white */
    .stApp {{
        background: {GOOGLE_WHITE};
    }}
    
    /* Centered container */
    .login-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 1rem;
        background: {GOOGLE_WHITE};
    }}
    
    /* Card styling - everything in one box */
    .card {{
        background: {GOOGLE_WHITE};
        border-radius: 16px;
        padding: 2rem;
        width: 100%;
        max-width: 460px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        border: 1px solid {GOOGLE_BORDER};
        animation: fadeIn 0.4s ease;
    }}
    
    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .title {{
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }}
    
    .subtitle {{
        color: {GOOGLE_DARK_GREY};
        font-size: 0.9rem;
        text-align: center;
        margin-bottom: 1rem;
    }}
    
    .chip {{
        background: {GOOGLE_LIGHT_GREY};
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        color: {GOOGLE_DARK_GREY};
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    .chip-dot {{
        width: 6px;
        height: 6px;
        background-color: {SPAR_GREEN};
        border-radius: 50%;
        display: inline-block;
    }}
    
    /* Toggle buttons */
    .toggle-container {{
        display: flex;
        gap: 1rem;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid {GOOGLE_BORDER};
    }}
    
    .toggle-btn {{
        flex: 1;
        text-align: center;
        padding: 0.75rem;
        cursor: pointer;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    /* Form styling */
    .stForm {{
        background: transparent;
    }}
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {{
        border-radius: 8px;
        border: 1px solid {GOOGLE_BORDER};
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        background: {GOOGLE_WHITE};
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {SPAR_RED};
        box-shadow: 0 0 0 2px rgba(227, 0, 15, 0.1);
    }}
    
    /* Button styling */
    .stButton > button {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-weight: 600;
        border-radius: 8px;
        width: 100%;
        transition: all 0.3s ease;
        margin-top: 0.5rem;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(227, 0, 15, 0.3);
    }}
    
    /* Secondary button */
    .secondary-btn > button {{
        background: transparent;
        color: {SPAR_RED};
        border: 1px solid {GOOGLE_BORDER};
    }}
    
    .secondary-btn > button:hover {{
        background: {GOOGLE_LIGHT_GREY};
        transform: none;
        box-shadow: none;
    }}
    
    /* Divider */
    .divider {{
        text-align: center;
        margin: 1.5rem 0;
        position: relative;
    }}
    
    .divider::before {{
        content: '';
        position: absolute;
        top: 50%;
        left: 0;
        right: 0;
        height: 1px;
        background: {GOOGLE_BORDER};
    }}
    
    .divider span {{
        background: {GOOGLE_WHITE};
        padding: 0 1rem;
        position: relative;
        color: {GOOGLE_DARK_GREY};
        font-size: 0.8rem;
    }}
    
    /* Main app header after login */
    .app-header {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    
    .app-header h1 {{
        margin: 0;
        font-size: 1.8rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    
    .app-header p {{
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }}
    
    .content-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
        border: 1px solid {GOOGLE_BORDER};
    }}
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background-color: white;
        padding: 0.5rem;
        border-radius: 12px;
        border: 1px solid {GOOGLE_BORDER};
        margin-bottom: 1rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        color: white;
    }}
    
    /* User info */
    .user-info {{
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 40px;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }}
    
    /* Alert messages */
    .stAlert {{
        border-radius: 8px;
        font-size: 0.85rem;
    }}
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# USER DATABASE
# -----------------------------
if 'users' not in st.session_state:
    st.session_state.users = {
        'admin@tengai.com': {
            'name': 'Administrator',
            'email': 'admin@tengai.com',
            'username': 'admin',
            'password': hashlib.sha256('Admin@123'.encode()).hexdigest(),
            'role': 'admin',
            'created_at': datetime.now().isoformat()
        }
    }
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "login"  # login or register
if 'sales_history' not in st.session_state:
    st.session_state.sales_history = []
if 'offline_queue' not in st.session_state:
    st.session_state.offline_queue = []

# -----------------------------
# AUTHENTICATION FUNCTIONS
# -----------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def register_user(name, username, email, password):
    if email in st.session_state.users:
        return False, "Email already registered"
    
    for user_email, user_data in st.session_state.users.items():
        if user_data['username'] == username:
            return False, "Username already taken"
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    st.session_state.users[email] = {
        'name': name,
        'email': email,
        'username': username,
        'password': hash_password(password),
        'role': 'user',
        'created_at': datetime.now().isoformat()
    }
    
    return True, "Registration successful! Please login."

def login_user(email, password):
    if email in st.session_state.users:
        user = st.session_state.users[email]
        if verify_password(password, user['password']):
            st.session_state.logged_in = True
            st.session_state.current_user = user
            return True, f"Welcome back, {user['name']}!"
    
    return False, "Invalid email or password"

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.active_tab = "login"

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

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
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #E3000F;">New SPAR Sale Recorded!</h2>
            <p><strong>Sale ID:</strong> {sale_id}</p>
            <p><strong>Customer:</strong> {customer_name}</p>
            <p><strong>Email:</strong> {customer_email if customer_email else 'Not provided'}</p>
            <p><strong>Product:</strong> {product}</p>
            <p><strong>Quantity:</strong> {quantity}</p>
            <p><strong>Total:</strong> ${total_sales:,.2f}</p>
            <p><strong>Rewards:</strong> {rewards_earned:.0f} points</p>
            <p><strong>Recorded by:</strong> {st.session_state.current_user['name']}</p>
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

# -----------------------------
# LOGIN/REGISTER SCREEN (Everything in one box)
# -----------------------------

def login_register_screen():
    """Display login and register in the same centered box"""
    
    st.markdown("""
    <div class="login-wrapper">
        <div class="card">
            <div class="title">Tengai</div>
            <div class="subtitle">Sign in to continue.</div>
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <div class="chip"><span class="chip-dot"></span> Version 3.3.0 • Production</div>
            </div>
    """, unsafe_allow_html=True)
    
    # Toggle buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In", use_container_width=True, 
                     type="primary" if st.session_state.active_tab == "login" else "secondary"):
            st.session_state.active_tab = "login"
            st.rerun()
    with col2:
        if st.button("Create Account", use_container_width=True,
                     type="primary" if st.session_state.active_tab == "register" else "secondary"):
            st.session_state.active_tab = "register"
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.active_tab == "login":
        # Login Form
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if email and password:
                    success, message = login_user(email, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter email and password")
        
        # Demo credentials hint
        st.caption("Demo: admin@tengai.com / Admin@123")
    
    else:
        # Registration Form
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name")
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Min 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                if not all([name, username, email, password]):
                    st.error("Please fill all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = register_user(name, username, email, password)
                    if success:
                        st.success(message)
                        st.session_state.active_tab = "login"
                        st.rerun()
                    else:
                        st.error(message)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# -----------------------------
# MAIN APP CONTENT (After Login)
# -----------------------------

def main_app():
    """Main application content after login"""
    
    # Header with user info and logout
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("""
        <div class="app-header">
            <h1>🎯 Tengai - SPAR Sales & Rewards System</h1>
            <p>Your trusted partner in retail excellence</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: right;">
            <div class="user-info">
                👋 {st.session_state.current_user['name']}<br>
                <small>({st.session_state.current_user['role'].upper()})</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Sign Out", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Record Sale", "🏆 Rewards Analysis", "📊 Dashboard", "⚙️ Settings"])
    
    # TAB 1: Record Sale
    with tab1:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
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
                st.markdown("**🛍️ Purchase Details**")
                
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
                    <div style="background: #F8F9FA; padding: 0.75rem; border-radius: 8px; text-align: center;">
                        <strong>💰 Total Amount:</strong> 
                        <span style="font-size: 1.3rem; color: #E3000F;">${total_sales:,.2f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                rewards_earned = total_sales * 0.02
                st.info(f"⭐ SPAR Rewards Points Earned: {rewards_earned:.0f} points (2% of purchase)")
                
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
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'recorded_by': st.session_state.current_user['name']
                        }
                        
                        success, message = send_to_webhook(data)
                        send_admin_notification(customer_name, sale_id, product, quantity, total_sales, rewards_earned, customer_email)
                        
                        if success:
                            st.success(f"✅ Sale recorded! ID: {sale_id}")
                            if send_receipt and customer_email:
                                st.info(f"📧 Receipt sent to {customer_email}")
                            st.balloons()
                        else:
                            st.warning(f"⚠️ Sale recorded but ETL offline: {message}")
                        
                        st.session_state.sales_history.insert(0, data)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("### 📊 System Status")
            
            if check_connection():
                st.success("✅ ETL Connected")
            else:
                st.warning("⚠️ ETL Offline")
            
            if st.session_state.sales_history:
                df = pd.DataFrame(st.session_state.sales_history)
                st.metric("Session Sales", f"${df['total_sales'].sum():,.2f}")
                st.metric("Transactions", len(df))
            
            st.markdown("---")
            st.caption("Data is sent to your local ETL system automatically")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: Rewards Analysis
    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.title("🏆 SPAR Rewards Analysis")
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} records")
            st.dataframe(df.head(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: Dashboard
    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.title("📊 Sales Dashboard")
        
        if st.session_state.sales_history:
            df = pd.DataFrame(st.session_state.sales_history)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sales", f"${df['total_sales'].sum():,.2f}")
            with col2:
                st.metric("Transactions", len(df))
            with col3:
                st.metric("Rewards Given", f"{df['rewards_earned'].sum():,.0f} pts")
            
            st.subheader("Recent Transactions")
            st.dataframe(df[['sale_id', 'customer_name', 'product', 'total_sales']].head(10), 
                        use_container_width=True, hide_index=True)
            
            csv = df.to_csv(index=False)
            st.download_button("📥 Download Data", csv, f"sales_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No sales recorded yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 4: Settings
    with tab4:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.title("⚙️ Settings")
        
        st.subheader("👤 My Profile")
        st.write(f"**Name:** {st.session_state.current_user['name']}")
        st.write(f"**Email:** {st.session_state.current_user['email']}")
        st.write(f"**Username:** {st.session_state.current_user['username']}")
        st.write(f"**Role:** {st.session_state.current_user['role'].capitalize()}")
        
        if st.session_state.current_user['role'] == 'admin':
            st.divider()
            st.subheader("👑 Admin Panel")
            with st.expander("View Registered Users"):
                users_list = []
                for email, user in st.session_state.users.items():
                    users_list.append({
                        'Name': user['name'],
                        'Email': email,
                        'Username': user['username'],
                        'Role': user['role']
                    })
                st.dataframe(pd.DataFrame(users_list), use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# MAIN
# -----------------------------

if st.session_state.logged_in:
    main_app()
else:
    login_register_screen()
