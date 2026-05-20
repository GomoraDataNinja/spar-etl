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
ORG_PASSWORD = "SPAR2024"  # Organisation password - change this!

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
GOOGLE_LIGHT_GREY = "#F5F5F5"
GOOGLE_DARK_GREY = "#5F6368"

# Custom CSS
st.markdown(f"""
    <style>
    /* Main app background */
    .stApp {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }}
    
    /* Card styling */
    .card {{
        background: {GOOGLE_WHITE};
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        text-align: center;
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
    
    .title {{
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }}
    
    .subtitle {{
        color: {GOOGLE_DARK_GREY};
        font-size: 0.9rem;
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
    
    /* Form styling */
    .stForm {{
        background: transparent;
    }}
    
    .stTextInput > div > div > input {{
        border-radius: 8px;
        border: 1px solid {GOOGLE_BORDER};
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
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
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(227, 0, 15, 0.3);
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
    
    /* Metric card */
    .metric-card {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        text-align: center;
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
    
    /* Success message */
    .success-message {{
        background: #d4edda;
        color: #155724;
        padding: 0.75rem;
        border-radius: 8px;
        margin: 1rem 0;
    }}
    
    /* Info box */
    .info-box {{
        background: #f8f9fa;
        padding: 0.75rem;
        border-radius: 8px;
        border-left: 4px solid {SPAR_GREEN};
    }}
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# SESSION STATE
# -----------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'sales_history' not in st.session_state:
    st.session_state.sales_history = []
if 'offline_queue' not in st.session_state:
    st.session_state.offline_queue = []

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def touch():
    """Update session timestamp"""
    st.session_state.last_activity = time.time()

def safe_rerun():
    """Safe rerun with small delay"""
    time.sleep(0.1)
    st.rerun()

def generate_sale_id():
    """Generate unique Sale ID"""
    return f"SPAR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def send_to_webhook(data):
    """Send data to local ETL via webhook"""
    try:
        response = requests.post(WEBHOOK_URL, json=data, timeout=10)
        if response.status_code == 200:
            return True, "Data sent to ETL"
        return False, f"Server error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to ETL server"
    except Exception as e:
        return False, str(e)

def send_admin_notification(customer_name, sale_id, product, quantity, total_sales, rewards_earned, customer_email=None):
    """Send email notification to admin"""
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
    """Test connection to ETL server"""
    try:
        response = requests.get(WEBHOOK_URL.replace('/webhook', '/health'), timeout=5)
        return response.status_code == 200
    except:
        return False

# -----------------------------
# LOGIN SCREEN
# -----------------------------

def login_screen():
    st.markdown('<div style="height: 1.8rem;"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.25, 1])
    with c2:
        st.markdown(
            f"""
            <div class="card" style="margin-top: 10vh;">
                <div class="title" style="text-align:center;">{APP_NAME}</div>
                <div class="subtitle" style="text-align:center;">Sign in to continue.</div>
                <div style="height: 14px;"></div>
                <div style="display:flex; justify-content:center;">
                    <div class="chip"><span class="chip-dot"></span> Version {APP_VERSION} • {DEPLOYMENT_MODE.title()}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=True):
            pw = st.text_input("Password", type="password", placeholder="Organisation password")
            ok = st.form_submit_button("Sign in", use_container_width=True)

        if ok:
            if pw == ORG_PASSWORD:
                st.session_state.authenticated = True
                touch()
                safe_rerun()
            else:
                st.error("Wrong password.")

# -----------------------------
# MAIN APP CONTENT
# -----------------------------

def main_app():
    """Main application content after login"""
    
    # Header
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
                👤 Admin • <a href="#" onclick="location.reload();" style="color: #E3000F; text-decoration: none;">Sign Out</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sign out button
        if st.button("🚪 Sign Out", use_container_width=True):
            st.session_state.authenticated = False
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
                    <div class="info-box" style="text-align: center;">
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
                            'recorded_by': 'Admin'
                        }
                        
                        # Send to webhook
                        success, message = send_to_webhook(data)
                        
                        # Send admin notification
                        send_admin_notification(customer_name, sale_id, product, quantity, total_sales, rewards_earned, customer_email)
                        
                        if success:
                            st.success(f"✅ Sale recorded successfully! Sale ID: {sale_id}")
                            if send_receipt and customer_email:
                                st.info(f"📧 Receipt sent to {customer_email}")
                            st.balloons()
                        else:
                            st.warning(f"⚠️ Sale recorded but not sent to ETL: {message}")
                        
                        # Store in history
                        st.session_state.sales_history.insert(0, data)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col_right:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.markdown("### 📊 System Status")
            
            if check_connection():
                st.success("✅ ETL Connected")
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
            st.caption("Data is sent to your local ETL system automatically")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 2: Rewards Analysis
    with tab2:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.title("🏆 SPAR Rewards Analysis")
        st.markdown("Upload your SPAR rewards CSV file to analyze customer behavior")
        
        uploaded_file = st.file_uploader("Choose CSV file", type=['csv'])
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.success(f"✅ Loaded {len(df)} records")
            st.dataframe(df.head(), use_container_width=True)
            
            # Basic statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Customers", df['CustomerID'].nunique())
            with col2:
                st.metric("Total Sales", f"${df['SalesAmount'].sum():,.2f}")
            with col3:
                st.metric("Total Rewards", f"{df['RewardsEarned'].sum():,.0f}")
        
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
                st.metric("Total Transactions", len(df))
            with col3:
                st.metric("Total Rewards", f"{df['rewards_earned'].sum():,.0f} pts")
            
            st.subheader("Recent Transactions")
            st.dataframe(df[['sale_id', 'customer_name', 'product', 'total_sales', 'timestamp']].head(10), 
                        use_container_width=True, hide_index=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Sales Data (CSV)",
                data=csv,
                file_name=f"tengai_sales_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No sales recorded yet. Start recording sales to see insights!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # TAB 4: Settings
    with tab4:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.title("⚙️ Settings")
        
        st.subheader("ℹ️ System Information")
        st.write(f"**App Name:** {APP_NAME}")
        st.write(f"**Version:** {APP_VERSION}")
        st.write(f"**Deployment:** {DEPLOYMENT_MODE.title()}")
        st.write(f"**Webhook URL:** {WEBHOOK_URL}")
        
        st.divider()
        
        st.subheader("📁 Data Management")
        if st.session_state.sales_history:
            st.write(f"**Sales in session:** {len(st.session_state.sales_history)}")
            if st.button("🗑️ Clear Session Data", use_container_width=True):
                st.session_state.sales_history = []
                st.session_state.offline_queue = []
                st.success("Session data cleared!")
                st.rerun()
        else:
            st.info("No session data")
        
        st.divider()
        
        st.subheader("🔌 Connection Test")
        if st.button("Test ETL Connection", use_container_width=True):
            if check_connection():
                st.success("✅ Successfully connected to ETL server!")
                st.info(f"Webhook URL: {WEBHOOK_URL}")
            else:
                st.error("❌ Cannot connect to ETL server")
                st.info("Make sure your tunnel is running: cloudflared tunnel --url http://localhost:8000")
        
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# MAIN
# -----------------------------

if st.session_state.authenticated:
    main_app()
else:
    login_screen()
