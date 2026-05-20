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
ADMIN_EMAIL = "gomoraefesto97@gmail.com"  # Hidden from users

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

# Custom CSS with centered box
st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
    }}
    
    /* Centered Container */
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
        max-width: 440px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
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
        font-weight: 700;
    }}
    
    .login-header p {{
        color: {SPAR_DARK_GRAY};
        font-size: 0.85rem;
    }}
    
    .login-header .version {{
        color: #999;
        font-size: 0.7rem;
        margin-top: 0.5rem;
    }}
    
    /* Form styling */
    .stForm {{
        background: transparent;
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
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        padding: 0.6rem;
        font-size: 0.9rem;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {SPAR_RED};
        box-shadow: 0 0 0 2px rgba(227, 0, 15, 0.1);
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
        background: #e0e0e0;
    }}
    
    .divider span {{
        background: white;
        padding: 0 1rem;
        position: relative;
        color: #999;
        font-size: 0.8rem;
    }}
    
    /* Toggle buttons for login/register */
    .toggle-buttons {{
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}
    
    .toggle-btn {{
        flex: 1;
        text-align: center;
        padding: 0.75rem;
        cursor: pointer;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .toggle-btn-active {{
        background-color: {SPAR_RED};
        color: white;
    }}
    
    .toggle-btn-inactive {{
        background-color: {SPAR_GRAY};
        color: {SPAR_DARK_GRAY};
    }}
    
    .spar-header {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
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
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    
    .success-message {{
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}
    
    .error-message {{
        background: #f8d7da;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# USER DATABASE
# -----------------------------
if 'users' not in st.session_state:
    st.session_state.users = {
        'gomoraefesto97@gmail.com': {
            'name': 'Admin User',
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
    st.session_state.show_register = False

# -----------------------------
# MAIN APP CONTENT
# -----------------------------

def main_app():
    """Main application content"""
    
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
    if 'sales_history' not in st.session_state:
        st.session_state.sales_history = []
    if 'offline_queue' not in st.session_state:
        st.session_state.offline_queue = []
    
    # Helper functions
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
                <h2>New SPAR Sale Recorded!</h2>
                <p><strong>Sale ID:</strong> {sale_id}</p>
                <p><strong>Customer:</strong> {customer_name}</p>
                <p><strong>Customer Email:</strong> {customer_email if customer_email else 'Not provided'}</p>
                <p><strong>Product:</strong> {product}</p>
                <p><strong>Quantity:</strong> {quantity}</p>
                <p><strong>Total Amount:</strong> ${total_sales:,.2f}</p>
                <p><strong>Rewards Earned:</strong> {rewards_earned:.0f} points</p>
                <p><strong>Recorded by:</strong> {st.session_state.current_user['name']} ({st.session_state.current_user['email']})</p>
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
                        "Bakery", "Beverages", "Household", "Personal Care", "Other"
                    ])
                    if product == "Other":
                        product = st.text_input("Specify Product")
                
                with col_f:
                    quantity = st.number_input("Quantity *", min_value=1, value=1, step=1)
                
                col_g, col_h = st.columns(2)
                with col_g:
                    unit_price = st.number_input("Unit Price (USD) *", min_value=0.01, value=99.99, step=0.01, format="%.2f")
                with col_h:
                    total_sales = quantity * unit_price
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>💰 Total Amount:</strong> <span style="font-size: 1.2rem;">${total_sales:,.2f} USD</span>
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
                            'recorded_by': st.session_state.current_user['name'],
                            'recorded_by_email': st.session_state.current_user['email']
                        }
                        
                        # Send to webhook
                        success, message = send_to_webhook(data)
                        
                        # Send admin notification
                        send_admin_notification(customer_name, sale_id, product, quantity, total_sales, rewards_earned, customer_email)
                        
                        if success:
                            st.success(f"✅ Sale recorded successfully! Sale ID: {sale_id}")
                            if send_receipt and customer_email:
                                st.info(f"📧 Receipt will be sent to {customer_email}")
                            st.balloons()
                        else:
                            st.warning(f"⚠️ Sale recorded but not sent to ETL: {message}")
                        
                        st.session_state.sales_history.insert(0, data)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="spar-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Today's Summary")
            
            if check_connection():
                st.success("✅ Connected to ETL")
            else:
                st.warning("⚠️ ETL Offline - Data will queue")
            
            if st.session_state.sales_history:
                df = pd.DataFrame(st.session_state.sales_history)
                st.metric("Session Sales", f"${df['total_sales'].sum():,.2f}")
                st.metric("Transactions", len(df))
                if len(df) > 0:
                    st.metric("Average Order", f"${df['total_sales'].mean():,.2f}")
            
            if st.session_state.offline_queue:
                st.error(f"📱 {len(st.session_state.offline_queue)} pending sync")
            
            st.markdown("---")
            st.markdown("### ℹ️ Info")
            st.caption("Sales data is sent to your local ETL system automatically")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: SPAR Rewards
    with tab2:
        st.markdown('<div class="spar-card">', unsafe_allow_html=True)
        st.title("🏆 SPAR Rewards Analysis")
        st.markdown("Upload your SPAR rewards CSV file to analyze customer behavior")
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} records")
            st.dataframe(df.head(), use_container_width=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 3: Dashboard
    with tab3:
        st.markdown('<div class="spar-card">', unsafe_allow_html=True)
        st.title("📊 Sales Dashboard")
        
        if st.session_state.sales_history:
            df = pd.DataFrame(st.session_state.sales_history)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Sales", f"${df['total_sales'].sum():,.2f}")
            with col2:
                st.metric("Total Transactions", len(df))
            with col3:
                st.metric("Total Rewards", f"{df['rewards_earned'].sum():,.0f} pts")
            
            st.subheader("Recent Transactions")
            st.dataframe(df[['sale_id', 'customer_name', 'product', 'total_sales', 'timestamp']].head(10), 
                        use_container_width=True, hide_index=True)
            
            csv = df.to_csv(index=False)
            st.download_button("📥 Download Sales Data", csv, f"sales_{datetime.now().strftime('%Y%m%d')}.csv")
        else:
            st.info("No sales recorded yet")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 4: Settings
    with tab4:
        st.markdown('<div class="spar-card">', unsafe_allow_html=True)
        st.title("⚙️ Settings")
        
        st.subheader("👤 My Profile")
        st.write(f"**Name:** {st.session_state.current_user['name']}")
        st.write(f"**Email:** {st.session_state.current_user['email']}")
        st.write(f"**Username:** {st.session_state.current_user['username']}")
        st.write(f"**Role:** {st.session_state.current_user['role'].capitalize()}")
        st.write(f"**Member since:** {st.session_state.current_user.get('created_at', 'N/A')[:10]}")
        
        # Admin-only section
        if st.session_state.current_user['role'] == 'admin':
            st.divider()
            st.subheader("👑 Admin Controls")
            
            with st.expander("📋 Registered Users"):
                users_list = []
                for email, user in st.session_state.users.items():
                    users_list.append({
                        'Name': user['name'],
                        'Email': email,
                        'Username': user['username'],
                        'Role': user['role'],
                        'Joined': user['created_at'][:10]
                    })
                if users_list:
                    st.dataframe(pd.DataFrame(users_list), use_container_width=True, hide_index=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# LOGIN PAGE WITH TOGGLE
# -----------------------------

def show_login_page():
    """Display centered login/register page"""
    
    st.markdown("""
    <div class="login-container">
        <div class="login-box">
            <div class="login-header">
                <h1>📚 Ruzivo</h1>
                <p>SPAR Sales & Rewards System</p>
                <div class="version">Version 3.3.0 • Production</div>
            </div>
    """, unsafe_allow_html=True)
    
    # Custom toggle using columns (no JavaScript)
    col_login, col_register = st.columns(2)
    
    with col_login:
        if st.button("Sign In", use_container_width=True, 
                     type="primary" if not st.session_state.show_register else "secondary"):
            st.session_state.show_register = False
            st.rerun()
    
    with col_register:
        if st.button("Create Account", use_container_width=True,
                     type="primary" if st.session_state.show_register else "secondary"):
            st.session_state.show_register = True
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.show_register:
        # Login Form
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your@email.com", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
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
    else:
        # Registration Form
        with st.form("register_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name", key="reg_name")
            username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
            email = st.text_input("Email", placeholder="your@email.com", key="reg_email")
            password = st.text_input("Password", type="password", placeholder="Min 6 characters", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
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
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error(message)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# -----------------------------
# MAIN
# -----------------------------

if st.session_state.logged_in:
    main_app()
else:
    show_login_page()
