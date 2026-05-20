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
import secrets

# Configure page
st.set_page_config(
    page_title="Ruzivo - SPAR Sales & Rewards System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# EMAIL CONFIGURATION
# ============================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"  # Update this
SENDER_PASSWORD = "your_app_password"  # Update this
ADMIN_EMAIL = "gomoraefesto97@gmail.com"  # Hardcoded admin email

# ============================================
# WEBHOOK URL (Update with your tunnel)
# ============================================
WEBHOOK_URL = "https://assessed-triumph-accessed-nam.trycloudflare.com/webhook"

# SPAR Brand Colours
SPAR_RED = "#E3000F"
SPAR_GREEN = "#007A3D"
SPAR_DARK_RED = "#C4000D"
SPAR_DARK_GREEN = "#005C2E"
SPAR_WHITE = "#FFFFFF"
SPAR_GRAY = "#F5F5F5"
SPAR_DARK_GRAY = "#666666"

# Custom CSS with centered login box
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
    }}
    
    /* Centered Login Box */
    .login-container {{
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        padding: 1rem;
    }}
    
    .login-box {{
        background: white;
        border-radius: 20px;
        padding: 2rem;
        width: 100%;
        max-width: 420px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        animation: fadeIn 0.5s ease;
    }}
    
    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(-20px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    
    .login-header {{
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    .login-header h1 {{
        color: {SPAR_RED};
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }}
    
    .login-header p {{
        color: {SPAR_DARK_GRAY};
        font-size: 0.9rem;
    }}
    
    .login-header .version {{
        color: #999;
        font-size: 0.75rem;
        margin-top: 0.5rem;
    }}
    
    .stButton > button {{
        background-color: {SPAR_RED};
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border-radius: 8px;
        width: 100%;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {SPAR_DARK_RED};
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(227, 0, 15, 0.3);
    }}
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {{
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        padding: 0.6rem;
        font-size: 0.95rem;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {SPAR_RED};
        box-shadow: 0 0 0 2px rgba(227, 0, 15, 0.1);
    }}
    
    .error-message {{
        background: #fee;
        color: {SPAR_RED};
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
    }}
    
    .success-message {{
        background: #e8f5e9;
        color: {SPAR_GREEN};
        padding: 0.75rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
    }}
    
    .spar-header {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }}
    
    .spar-card {{
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border-top: 4px solid {SPAR_RED};
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
    }}
    
    .info-box {{
        background: {SPAR_GRAY};
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid {SPAR_GREEN};
    }}
    
    .user-info {{
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin-bottom: 1rem;
    }}
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# USER DATABASE (In-memory - for demo)
# In production, use a real database
# -----------------------------
if 'users' not in st.session_state:
    st.session_state.users = {
        # Pre-create admin user
        'admin@ruzivo.com': {
            'name': 'Admin',
            'email': 'gomoraefesto97@gmail.com',
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
if 'show_register' not in st.session_state:
    st.session_state.show_register = False

# -----------------------------
# AUTHENTICATION FUNCTIONS
# -----------------------------

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    """Verify password against hash"""
    return hash_password(password) == hashed

def register_user(name, username, email, password):
    """Register a new user"""
    if email in st.session_state.users:
        return False, "Email already registered"
    
    # Check if username exists
    for user_email, user_data in st.session_state.users.items():
        if user_data['username'] == username:
            return False, "Username already taken"
    
    # Validate email format
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format"
    
    # Validate password strength
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    # Create user
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
    """Authenticate user"""
    if email in st.session_state.users:
        user = st.session_state.users[email]
        if verify_password(password, user['password']):
            st.session_state.logged_in = True
            st.session_state.current_user = user
            return True, f"Welcome back, {user['name']}!"
    
    # Check if it's the hardcoded admin email
    if email == ADMIN_EMAIL and password == "Admin@123":
        # Create admin if not exists
        if email not in st.session_state.users:
            register_user("System Admin", "admin", email, "Admin@123")
            st.session_state.users[email]['role'] = 'admin'
        
        st.session_state.logged_in = True
        st.session_state.current_user = st.session_state.users[email]
        return True, "Welcome Admin!"
    
    return False, "Invalid email or password"

def logout_user():
    """Log out current user"""
    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.show_register = False

# -----------------------------
# MAIN APP CONTENT (shown after login)
# -----------------------------

def main_app():
    """Main application content - shown after successful login"""
    
    # User info bar
    col_user, col_logout = st.columns([4, 1])
    with col_user:
        st.markdown(f"""
        <div class="user-info">
            👋 Welcome, <strong>{st.session_state.current_user['name']}</strong> 
            ({st.session_state.current_user['role'].upper()})
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    st.markdown("""
    <div class="spar-header">
        <h1>📚 Ruzivo - SPAR Sales & Rewards System</h1>
        <p>Your trusted partner in retail excellence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for app data
    if 'rewards_analysis_complete' not in st.session_state:
        st.session_state.rewards_analysis_complete = None
    if 'rewards_results' not in st.session_state:
        st.session_state.rewards_results = None
    if 'uploaded_filename' not in st.session_state:
        st.session_state.uploaded_filename = None
    if 'selected_customer' not in st.session_state:
        st.session_state.selected_customer = None
    if 'offline_queue' not in st.session_state:
        st.session_state.offline_queue = []
    if 'sales_history' not in st.session_state:
        st.session_state.sales_history = []
    if 'email_notifications_enabled' not in st.session_state:
        st.session_state.email_notifications_enabled = True
    
    # Helper functions
    def generate_sale_id():
        return f"SPAR-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def send_to_webhook(data):
        try:
            response = requests.post(WEBHOOK_URL, json=data, timeout=10)
            if response.status_code == 200:
                return True, "Data sent to ETL successfully"
            return False, f"Server returned: {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def send_customer_receipt(customer_email, customer_name, sale_id, product, quantity, unit_price, total_sales, rewards_earned):
        if not customer_email:
            return False, "No email provided"
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = customer_email
            msg['Subject'] = f"Thank you for shopping at SPAR! Receipt {sale_id}"
            
            html_content = f"""
            <html>
            <body>
                <div style="background: linear-gradient(135deg, #E3000F 0%, #007A3D 100%); padding: 20px; text-align: center; color: white;">
                    <h1>🛒 SPAR</h1>
                </div>
                <div style="padding: 20px;">
                    <h2>Thank you, {customer_name}!</h2>
                    <p><strong>Receipt:</strong> {sale_id}</p>
                    <p><strong>Product:</strong> {product}</p>
                    <p><strong>Quantity:</strong> {quantity}</p>
                    <p><strong>Total:</strong> ${total_sales:,.2f}</p>
                    <p><strong>Rewards Earned:</strong> {rewards_earned:.0f} points</p>
                </div>
            </body>
            </html>
            """
            msg.attach(MIMEText(html_content, 'html'))
            
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            return True, "Receipt sent"
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
                <h2>New SPAR Sale!</h2>
                <p><strong>Sale ID:</strong> {sale_id}</p>
                <p><strong>Customer:</strong> {customer_name}</p>
                <p><strong>Email:</strong> {customer_email}</p>
                <p><strong>Product:</strong> {product}</p>
                <p><strong>Quantity:</strong> {quantity}</p>
                <p><strong>Total:</strong> ${total_sales:,.2f}</p>
                <p><strong>Rewards:</strong> {rewards_earned:.0f} points</p>
                <p><strong>Recorded by:</strong> {st.session_state.current_user['name']}</p>
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
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Record Sale", "🏆 SPAR Rewards", "📊 Dashboard", "⚙️ Settings"])
    
    # TAB 1: Record Sale
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="spar-card">', unsafe_allow_html=True)
            sale_id = generate_sale_id()
            
            with st.form(key="sales_form", clear_on_submit=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    customer_name = st.text_input("Customer Name *")
                with col_b:
                    customer_email = st.text_input("Email Address")
                    send_receipt = st.checkbox("📧 Send receipt", value=True)
                
                col_c, col_d = st.columns(2)
                with col_c:
                    customer_id = st.text_input("SPAR Rewards ID")
                with col_d:
                    phone = st.text_input("Phone Number")
                
                st.markdown("---")
                col_e, col_f = st.columns(2)
                with col_e:
                    product = st.selectbox("Product *", ["Fresh Produce", "Meat & Poultry", "Dairy", "Bakery", "Beverages", "Household", "Personal Care"])
                with col_f:
                    quantity = st.number_input("Quantity *", min_value=1, value=1)
                
                col_g, col_h = st.columns(2)
                with col_g:
                    unit_price = st.number_input("Unit Price (USD) *", min_value=0.01, value=99.99, format="%.2f")
                with col_h:
                    total_sales = quantity * unit_price
                    st.markdown(f"💰 Total: **${total_sales:,.2f}**")
                
                rewards_earned = total_sales * 0.02
                st.info(f"⭐ Rewards Points: {rewards_earned:.0f} (2% of purchase)")
                
                submitted = st.form_submit_button("💾 Record Sale")
                
                if submitted and customer_name and product:
                    data = {
                        'sale_id': sale_id,
                        'customer_name': customer_name,
                        'customer_email': customer_email,
                        'product': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_sales': total_sales,
                        'rewards_earned': rewards_earned,
                        'timestamp': datetime.now().isoformat(),
                        'recorded_by': st.session_state.current_user['name']
                    }
                    
                    success, msg = send_to_webhook(data)
                    
                    if send_receipt and customer_email:
                        send_customer_receipt(customer_email, customer_name, sale_id, product, quantity, unit_price, total_sales, rewards_earned)
                    
                    send_admin_notification(customer_name, sale_id, product, quantity, total_sales, rewards_earned, customer_email)
                    
                    if success:
                        st.success(f"✅ Sale recorded! ID: {sale_id}")
                        st.balloons()
                    else:
                        st.warning(f"⚠️ Sale recorded but not sent to ETL: {msg}")
                    
                    st.session_state.sales_history.insert(0, data)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="spar-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Connection Status")
            if check_connection():
                st.success("✅ ETL Connected")
            else:
                st.warning("⚠️ ETL Offline")
            
            if st.session_state.sales_history:
                df = pd.DataFrame(st.session_state.sales_history)
                st.metric("Session Sales", f"${df['total_sales'].sum():,.2f}")
                st.metric("Transactions", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: SPAR Rewards (simplified)
    with tab2:
        st.markdown('<div class="spar-card">', unsafe_allow_html=True)
        st.title("🏆 SPAR Rewards Analysis")
        uploaded_file = st.file_uploader("Upload Rewards CSV", type=['csv'])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: Dashboard
    with tab3:
        st.markdown('<div class="spar-card">', unsafe_allow_html=True)
        st.title("📊 Dashboard")
        if st.session_state.sales_history:
            df = pd.DataFrame(st.session_state.sales_history)
            st.dataframe(df)
            csv = df.to_csv(index=False)
            st.download_button("Download Data", csv, "sales_data.csv")
        else:
            st.info("No sales recorded yet")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 4: Settings
    with tab4:
        st.markdown('<div class="spar-card">', unsafe_allow_html=True)
        st.title("⚙️ Settings")
        st.write(f"**Logged in as:** {st.session_state.current_user['name']}")
        st.write(f"**Email:** {st.session_state.current_user['email']}")
        st.write(f"**Role:** {st.session_state.current_user['role']}")
        st.write(f"**Member since:** {st.session_state.current_user.get('created_at', 'N/A')}")
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# LOGIN PAGE
# -----------------------------

def show_login_page():
    """Display centered login page"""
    
    st.markdown("""
    <div class="login-container">
        <div class="login-box">
            <div class="login-header">
                <h1>📚 Ruzivo</h1>
                <p>SPAR Sales & Rewards System</p>
                <div class="version">Version 3.3.0 • Production</div>
            </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.show_register:
        # Login Form
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Sign In", use_container_width=True)
            with col2:
                if st.form_submit_button("Create Account", use_container_width=True):
                    st.session_state.show_register = True
                    st.rerun()
            
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
        
        # Hardcoded admin hint
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem; font-size: 0.8rem; color: #999;">
            <p>Admin: gomoraefesto97@gmail.com</p>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Registration Form
        with st.form("register_form"):
            st.markdown("### Create Account")
            name = st.text_input("Full Name", placeholder="Enter your full name")
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Min 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Register", use_container_width=True)
            with col2:
                if st.form_submit_button("Back to Login", use_container_width=True):
                    st.session_state.show_register = False
                    st.rerun()
            
            if submitted:
                if not all([name, username, email, password]):
                    st.error("Please fill all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = register_user(name, username, email, password)
                    if success:
                        st.success(message)
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error(message)
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1rem; font-size: 0.8rem; color: #999;">
            <p>By creating an account, you agree to our terms</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# -----------------------------
# MAIN
# -----------------------------

if st.session_state.logged_in:
    main_app()
else:
    show_login_page()
