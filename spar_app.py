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
import gspread
from google.oauth2.service_account import Credentials

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
# WEBHOOK URL (Update with your tunnel)
# ============================================
WEBHOOK_URL = "https://kitchen-council-identification-technological.trycloudflare.com/webhook"

# ============================================
# GOOGLE SHEETS SETUP
# ============================================

def get_google_sheets_client():
    """Get Google Sheets client using credentials from secrets or local file"""
    try:
        # For Streamlit Cloud - use secrets
        if 'google' in st.secrets:
            creds_dict = dict(st.secrets["google"])
            creds = Credentials.from_service_account_info(
                creds_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            )
        else:
            # For local development - use JSON file
            creds = Credentials.from_service_account_file(
                'credentials.json',
                scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
            )
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        st.error(f"Google Sheets connection error: {e}")
        return None

def init_users_sheet():
    """Initialize the users sheet if it doesn't exist"""
    client = get_google_sheets_client()
    if client:
        try:
            # Try to open existing sheet
            sheet = client.open("Tengai_Users").sheet1
        except:
            # Create new sheet
            sheet = client.create("Tengai_Users").sheet1
            # Add headers
            sheet.append_row(["Email", "Name", "Username", "Password", "Role", "Created At"])
            
            # Add default admin
            sheet.append_row([
                "admin@tengai.com",
                "Administrator",
                "admin",
                hashlib.sha256("Admin@123".encode()).hexdigest(),
                "admin",
                datetime.now().isoformat()
            ])
        return sheet
    return None

def get_all_users():
    """Get all users from Google Sheets"""
    sheet = init_users_sheet()
    if sheet:
        records = sheet.get_all_records()
        users = {}
        for record in records:
            email = record.get('Email')
            if email:
                users[email] = {
                    'name': record.get('Name', ''),
                    'email': email,
                    'username': record.get('Username', ''),
                    'password': record.get('Password', ''),
                    'role': record.get('Role', 'user'),
                    'created_at': record.get('Created At', datetime.now().isoformat())
                }
        return users
    return {}

def save_user_to_sheet(email, name, username, password_hash, role):
    """Save a new user to Google Sheets"""
    sheet = init_users_sheet()
    if sheet:
        sheet.append_row([
            email,
            name,
            username,
            password_hash,
            role,
            datetime.now().isoformat()
        ])
        return True
    return False

# ============================================
# AUTHENTICATION FUNCTIONS
# ============================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def register_user(name, username, email, password):
    # Get current users
    users = get_all_users()
    
    # Check if email exists
    if email in users:
        return False, "Email already registered"
    
    # Check if username exists
    for user_email, user_data in users.items():
        if user_data['username'] == username:
            return False, "Username already taken"
    
    # Validate
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Determine role (first user becomes admin)
    role = "admin" if len(users) == 0 else "user"
    
    # Save to Google Sheets
    password_hash = hash_password(password)
    success = save_user_to_sheet(email, name, username, password_hash, role)
    
    if success:
        return True, f"Registration successful! You are the {role}."
    else:
        return False, "Registration failed. Please try again."

def login_user(email, password):
    users = get_all_users()
    
    if email in users:
        user = users[email]
        if verify_password(password, user['password']):
            st.session_state.logged_in = True
            st.session_state.current_user = user
            return True, f"Welcome back, {user['name']}!"
    
    return False, "Invalid email or password"

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.active_tab = "login"

# Configure page
st.set_page_config(
    page_title="Tengai - SPAR Sales & Rewards System",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# SPAR Brand Colours
SPAR_RED = "#E3000F"
SPAR_GREEN = "#007A3D"
SPAR_DARK_RED = "#C4000D"

# Modern colours
GOOGLE_WHITE = "#FFFFFF"
GOOGLE_BORDER = "#E0E0E0"
GOOGLE_LIGHT_GREY = "#F5F5F5"
GOOGLE_DARK_GREY = "#666666"

# Custom CSS
st.markdown(f"""
    <style>
    .stApp {{
        background: {GOOGLE_WHITE};
    }}
    
    .main-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 1rem;
        background: {GOOGLE_WHITE};
    }}
    
    .main-card {{
        background: {GOOGLE_WHITE};
        border-radius: 12px;
        padding: 1.5rem 2rem 1.5rem 2rem;
        width: 100%;
        max-width: 400px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border-left: 4px solid {SPAR_RED};
        border-right: 4px solid {SPAR_RED};
        border-top: 1px solid {GOOGLE_BORDER};
        border-bottom: 1px solid {GOOGLE_BORDER};
        animation: fadeIn 0.4s ease;
    }}
    
    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .title {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {SPAR_RED};
        text-align: center;
        margin-bottom: 0.1rem;
        line-height: 1.2;
    }}
    
    .subtitle {{
        color: {GOOGLE_DARK_GREY};
        font-size: 0.8rem;
        text-align: center;
        margin-bottom: 0.5rem;
    }}
    
    .chip-container {{
        text-align: center;
        margin-bottom: 0.8rem;
    }}
    
    .chip {{
        background: {GOOGLE_LIGHT_GREY};
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.65rem;
        color: {GOOGLE_DARK_GREY};
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }}
    
    .chip-dot {{
        width: 5px;
        height: 5px;
        background-color: {SPAR_GREEN};
        border-radius: 50%;
        display: inline-block;
    }}
    
    .stForm {{
        background: transparent;
    }}
    
    .stTextInput > div > div > input {{
        border-radius: 8px;
        border: 1px solid {GOOGLE_BORDER};
        padding: 0.5rem 0.8rem;
        font-size: 0.85rem;
        background: {GOOGLE_WHITE};
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {SPAR_RED};
        box-shadow: 0 0 0 2px rgba(227, 0, 15, 0.1);
    }}
    
    .stButton > button {{
        background-color: {SPAR_RED};
        color: white;
        border: none;
        padding: 0.5rem;
        font-weight: 600;
        border-radius: 8px;
        width: 100%;
        transition: all 0.2s ease;
        font-size: 0.85rem;
    }}
    
    .stButton > button:hover {{
        background-color: {SPAR_DARK_RED};
        transform: translateY(-1px);
    }}
    
    div[data-testid="column"]:has(button[kind="secondary"]) button {{
        background-color: transparent;
        color: {SPAR_RED};
        border: 1px solid {GOOGLE_BORDER};
    }}
    
    div[data-testid="column"]:has(button[kind="secondary"]) button:hover {{
        background-color: {GOOGLE_LIGHT_GREY};
        transform: none;
    }}
    
    .divider {{
        text-align: center;
        margin: 0.8rem 0;
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
        padding: 0 0.8rem;
        position: relative;
        color: {GOOGLE_DARK_GREY};
        font-size: 0.7rem;
    }}
    
    .footer-text {{
        text-align: center;
        font-size: 0.65rem;
        color: {GOOGLE_DARK_GREY};
        margin-top: 0.8rem;
    }}
    
    .app-header {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }}
    
    .app-header h1 {{
        margin: 0;
        font-size: 1.3rem;
    }}
    
    .app-header p {{
        margin: 0.2rem 0 0 0;
        opacity: 0.9;
        font-size: 0.75rem;
    }}
    
    .content-card {{
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
        border: 1px solid {GOOGLE_BORDER};
        border-left: 3px solid {SPAR_RED};
    }}
    
    .user-info {{
        background: white;
        padding: 0.3rem 0.8rem;
        border-radius: 30px;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        font-size: 0.75rem;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.3rem;
        background-color: white;
        padding: 0.3rem;
        border-radius: 10px;
        border: 1px solid {GOOGLE_BORDER};
        margin-bottom: 1rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 6px;
        padding: 0.3rem 0.8rem;
        font-size: 0.8rem;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {SPAR_RED};
        color: white;
    }}
    
    .row-widget.stSelectbox, .row-widget.stNumberInput {{
        margin-bottom: 0.3rem;
    }}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
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
    st.markdown("""
    <div class="main-container">
        <div class="main-card">
            <div class="title">Tengai</div>
            <div class="subtitle">Sign in to continue.</div>
            <div class="chip-container">
                <div class="chip"><span class="chip-dot"></span> Version 3.3.0 • Production</div>
            </div>
    """, unsafe_allow_html=True)
    
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
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if email and password:
                    success, message = login_user(email, password)
                    if success:
                        st.success(message)
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter email and password")
    else:
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
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(message)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# ============================================
# MAIN APP CONTENT
# ============================================

def main_app():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="app-header">
            <h1>🛒 Tengai - SPAR Sales & Rewards System</h1>
            <p>Your trusted partner in retail excellence</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="text-align: right;">
            <div class="user-info">
                👋 {st.session_state.current_user['name']} ({st.session_state.current_user['role'].upper()})
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            logout_user()
            st.rerun()
    
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
                    <div style="background: #F8F9FA; padding: 0.5rem; border-radius: 8px; text-align: center;">
                        <strong>💰 Total:</strong> <span style="font-size: 1.1rem; color: #E3000F;">${total_sales:,.2f}</span>
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
            st.markdown("### 📊 Status")
            
            if check_connection():
                st.success("✅ ETL Connected")
            else:
                st.warning("⚠️ ETL Offline")
            
            if st.session_state.sales_history:
                df = pd.DataFrame(st.session_state.sales_history)
                st.metric("Session Sales", f"${df['total_sales'].sum():,.2f}")
                st.metric("Transactions", len(df))
            
            st.markdown("---")
            st.caption("Data sent to your local ETL")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: Rewards Analysis
    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.title("🏆 Rewards Analysis")
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} records")
            st.dataframe(df.head(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: Dashboard
    with tab3:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.title("Sales Dashboard")
        
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
            with st.expander("Registered Users"):
                users = get_all_users()
                if users:
                    users_list = []
                    for email, user in users.items():
                        users_list.append({
                            'Name': user['name'],
                            'Email': email,
                            'Username': user['username'],
                            'Role': user['role'],
                            'Joined': user['created_at'][:10] if user['created_at'] else 'N/A'
                        })
                    st.dataframe(pd.DataFrame(users_list), use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN
# ============================================

if st.session_state.logged_in:
    main_app()
else:
    login_register_screen()
