import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import re
import plotly.express as px
import plotly.graph_objects as go
import requests
import json
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="SPAR Sales & Rewards System",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# IMPORTANT: UPDATE THIS WITH YOUR TUNNEL URL
# ============================================
# Get this from your Cloudflare Quick Tunnel:
# https://assessed-triumph-accessed-nam.trycloudflare.com
WEBHOOK_URL = "https://assessed-triumph-accessed-nam.trycloudflare.com/webhook"
# ============================================

# SPAR Brand Colours
SPAR_RED = "#E3000F"
SPAR_GREEN = "#007A3D"
SPAR_DARK_RED = "#C4000D"
SPAR_DARK_GREEN = "#005C2E"
SPAR_WHITE = "#FFFFFF"
SPAR_GRAY = "#F5F5F5"
SPAR_DARK_GRAY = "#666666"

# Custom CSS with SPAR branding
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {SPAR_GRAY};
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
    
    .spar-header h1 {{
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }}
    
    .spar-header p {{
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }}
    
    .spar-card {{
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border-top: 4px solid {SPAR_RED};
    }}
    
    .spar-card-green {{
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        border-top: 4px solid {SPAR_GREEN};
    }}
    
    .stButton > button {{
        background-color: {SPAR_RED};
        color: white;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        width: 100%;
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
        padding: 0.5rem;
        font-size: 0.95rem;
    }}
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {{
        border-color: {SPAR_RED};
        box-shadow: 0 0 0 2px rgba(227, 0, 15, 0.1);
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, {SPAR_RED} 0%, {SPAR_GREEN} 100%);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    
    .metric-card h3 {{
        margin: 0;
        font-size: 0.85rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .metric-card p {{
        margin: 0.5rem 0 0 0;
        font-size: 1.8rem;
        font-weight: bold;
    }}
    
    .success-message {{
        background: linear-gradient(135deg, {SPAR_GREEN} 0%, #00A859 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        animation: slideIn 0.5s ease;
        margin: 1rem 0;
    }}
    
    @keyframes slideIn {{
        from {{
            transform: translateY(-20px);
            opacity: 0;
        }}
        to {{
            transform: translateY(0);
            opacity: 1;
        }}
    }}
    
    .warning-message {{
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1rem;
        background-color: white;
        padding: 0.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        color: {SPAR_DARK_GRAY};
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {SPAR_RED};
        color: white;
    }}
    
    .info-box {{
        background: {SPAR_GRAY};
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid {SPAR_GREEN};
        margin: 1rem 0;
    }}
    
    .spar-footer {{
        text-align: center;
        padding: 1.5rem;
        color: {SPAR_DARK_GRAY};
        font-size: 0.85rem;
        border-top: 1px solid #e0e0e0;
        margin-top: 2rem;
    }}
    
    .upload-box {{
        border: 2px dashed {SPAR_RED};
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: {SPAR_GRAY};
    }}
    
    .welcome-text {{
        text-align: center;
        margin-bottom: 1.5rem;
    }}
    
    .welcome-text h2 {{
        color: {SPAR_RED};
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }}
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# INITIALIZE SESSION STATE
# -----------------------------
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
if 'last_sync_status' not in st.session_state:
    st.session_state.last_sync_status = ""
if 'sales_history' not in st.session_state:
    st.session_state.sales_history = []

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def generate_sale_id():
    """Generate unique Sale ID based on timestamp"""
    return f"SPAR-{datetime.now().strftime('%Y%m%d%H%M%S')}"

def send_to_webhook(data):
    """Send data to local ETL via webhook"""
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=data,
            timeout=10,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return True, "Data sent to ETL successfully"
        else:
            return False, f"Server returned: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to ETL server (tunnel may be down)"
    except requests.exceptions.Timeout:
        return False, "Connection timeout - ETL server slow"
    except Exception as e:
        return False, f"Error: {str(e)}"

def process_rewards_analysis(df):
    """Perform complete rewards analysis using your original logic"""
    
    df['TransactionDate'] = pd.to_datetime(df['Transaction Date'])
    today_date = df['TransactionDate'].max()
    
    customer_df = df.groupby('CustomerID').agg({
        'TransactionDate': lambda x: (today_date - x.max()).days,
        'ReceiptNumber': 'nunique',
        'SalesAmount': 'sum',
        'RewardsEarned': 'sum',
        'RewardsRedeemed': 'sum'
    }).reset_index()
    
    customer_df.columns = [
        'CustomerID', 'Recency', 'Frequency', 'Monetary',
        'RewardsEarned', 'RewardsRedeemed'
    ]
    
    try:
        customer_df['R_score'] = pd.qcut(customer_df['Recency'], 5, labels=[5,4,3,2,1])
        customer_df['F_score'] = pd.qcut(customer_df['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
        customer_df['M_score'] = pd.qcut(customer_df['Monetary'], 5, labels=[1,2,3,4,5])
    except:
        customer_df['R_score'] = customer_df['Recency'].rank(pct=True).apply(lambda x: 5 if x <= 0.2 else 4 if x <= 0.4 else 3 if x <= 0.6 else 2 if x <= 0.8 else 1)
        customer_df['F_score'] = customer_df['Frequency'].rank(pct=True).apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5)
        customer_df['M_score'] = customer_df['Monetary'].rank(pct=True).apply(lambda x: 1 if x <= 0.2 else 2 if x <= 0.4 else 3 if x <= 0.6 else 4 if x <= 0.8 else 5)
    
    customer_df['RFM_Score'] = (
        customer_df['R_score'].astype(int) +
        customer_df['F_score'].astype(int) +
        customer_df['M_score'].astype(int)
    )
    
    def segment_customer(row):
        if row['RFM_Score'] >= 12:
            return '👑 SPAR Loyal'
        elif row['Recency'] > 30 and row['Frequency'] > 3:
            return '⚠️ At Risk'
        elif row['Frequency'] == 1:
            return '🆕 One-Time Customer'
        elif row['Recency'] <= 7:
            return '✨ New Customer'
        else:
            return '📊 Regular Customer'
    
    customer_df['Segment'] = customer_df.apply(segment_customer, axis=1)
    
    def churn_score(row):
        score = 0
        if row['Recency'] > 30:
            score += 40
        if row['Frequency'] < 2:
            score += 30
        if row['Monetary'] < 50:
            score += 30
        return min(score, 100)
    
    customer_df['ChurnRisk'] = customer_df.apply(churn_score, axis=1)
    
    def recommend_action(row):
        if row['Segment'] == '👑 SPAR Loyal':
            return '🎁 Reward VIP perks - 20% discount on next purchase'
        elif row['Segment'] == '⚠️ At Risk':
            return '📧 Send retention offer - 15% off to bring them back'
        elif row['Segment'] == '🆕 One-Time Customer':
            return '🎫 Send comeback promo - 10% off second purchase'
        elif row['Segment'] == '✨ New Customer':
            return '🤝 Encourage second purchase with free delivery'
        elif row['RewardsEarned'] > row['RewardsRedeemed']:
            return f'⭐ Push reward redemption - {row["RewardsEarned"] - row["RewardsRedeemed"]:.0f} points available'
        else:
            return '📈 Monitor and engage with weekly offers'
    
    customer_df['RecommendedAction'] = customer_df.apply(recommend_action, axis=1)
    
    return customer_df

# -----------------------------
# CHECK CONNECTION FUNCTION
# -----------------------------
def check_connection():
    """Test connection to ETL server"""
    try:
        response = requests.get(WEBHOOK_URL.replace('/webhook', '/health'), timeout=5)
        return response.status_code == 200
    except:
        return False

# -----------------------------
# SPAR HEADER
# -----------------------------
st.markdown("""
<div class="spar-header">
    <h1>🛒 SPAR Sales & Rewards System</h1>
    <p>Cloud-Powered Sales Recording with Local ETL Integration</p>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# CONNECTION STATUS BAR
# -----------------------------
col_status, col_offline = st.columns([3, 1])

with col_status:
    is_connected = check_connection()
    if is_connected:
        st.success("✅ Connected to ETL System - Data will be sent to your local server")
    else:
        st.warning("⚠️ Offline Mode - Data will be saved locally and synced when connection resumes")

with col_offline:
    if len(st.session_state.offline_queue) > 0:
        st.error(f"📱 {len(st.session_state.offline_queue)} pending sync")
    if st.session_state.sales_history:
        st.info(f"📊 {len(st.session_state.sales_history)} sales this session")

# -----------------------------
# MAIN CONTENT WITH TABS
# -----------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📝 Record Sale", "🏆 SPAR Rewards", "📊 Dashboard", "⚙️ Settings"])

# -----------------------------
# TAB 1: RECORD SALE
# -----------------------------
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="welcome-text">
            <h2>Welcome to SPAR</h2>
            <p>Record customer purchases and earn rewards points</p>
        </div>
        """, unsafe_allow_html=True)
        
        sale_id = generate_sale_id()
        
        with st.container():
            st.markdown('<div class="spar-card">', unsafe_allow_html=True)
            
            with st.form(key="spar_sales_form", clear_on_submit=True):
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
                    product = st.selectbox(
                        "Product *",
                        ["Select product", "Fresh Produce", "Meat & Poultry", "Dairy", 
                         "Bakery", "Beverages", "Household", "Personal Care", "Other"]
                    )
                    
                    if product == "Other":
                        product = st.text_input("Specify Product", placeholder="Enter product name")
                    elif product == "Select product":
                        product = ""
                
                with col_f:
                    quantity = st.number_input("Quantity *", min_value=1, value=1, step=1)
                
                col_g, col_h = st.columns(2)
                
                with col_g:
                    unit_price = st.number_input("Unit Price (USD) *", min_value=0.01, value=99.99, step=0.01, format="%.2f")
                
                with col_h:
                    total_sales = quantity * unit_price
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>💰 Total Amount:</strong> <span style="font-size: 1.2rem;">${total_sales:,.2f} USD</span><br>
                        <small>Sale ID: {sale_id} | {quantity} × ${unit_price:,.2f}</small>
                    </div>
                    """, unsafe_allow_html=True)
                
                rewards_earned = total_sales * 0.02
                st.markdown(f"""
                <div style="background: #E8F5E9; padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
                    ⭐ <strong>SPAR Rewards Points Earned:</strong> {rewards_earned:.0f} points
                    <small>(2% of purchase value)</small>
                </div>
                """, unsafe_allow_html=True)
                
                submitted = st.form_submit_button("💾 Record Sale", use_container_width=True)
                
                if submitted:
                    if not customer_name:
                        st.error("❌ Please enter customer name")
                    elif not product or product == "Select product":
                        st.error("❌ Please select a product")
                    elif quantity <= 0 or unit_price <= 0:
                        st.error("❌ Please enter valid quantity and price")
                    else:
                        # Prepare data
                        data = {
                            'sale_id': sale_id,
                            'customer_name': customer_name,
                            'customer_email': customer_email,
                            'customer_id': customer_id if customer_id else '',
                            'phone': phone,
                            'product': product,
                            'quantity': quantity,
                            'unit_price': unit_price,
                            'total_sales': total_sales,
                            'rewards_earned': rewards_earned,
                            'timestamp': datetime.now().isoformat(),
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'month': datetime.now().strftime('%b').upper(),
                            'year': datetime.now().year
                        }
                        
                        # Try to send to webhook
                        success, message = send_to_webhook(data)
                        
                        if success:
                            st.markdown(f"""
                            <div class="success-message">
                                ✅ Sale recorded successfully!<br>
                                <strong>Sale ID:</strong> {sale_id}<br>
                                <strong>Customer:</strong> {customer_name}<br>
                                <strong>Total:</strong> ${total_sales:,.2f} USD<br>
                                <strong>Status:</strong> Sent to ETL system
                            </div>
                            """, unsafe_allow_html=True)
                            st.balloons()
                            st.session_state.last_sync_status = "✅ Last sale sent successfully"
                            # Store in history
                            st.session_state.sales_history.insert(0, data)
                        else:
                            # Save to offline queue
                            st.session_state.offline_queue.append(data)
                            st.markdown(f"""
                            <div class="warning-message">
                                ⚠️ Sale recorded but NOT sent to ETL!<br>
                                <strong>Sale ID:</strong> {sale_id}<br>
                                <strong>Customer:</strong> {customer_name}<br>
                                <strong>Total:</strong> ${total_sales:,.2f}<br>
                                <strong>Issue:</strong> {message}<br>
                                <strong>Action:</strong> Data saved to offline queue. Will retry automatically.
                            </div>
                            """, unsafe_allow_html=True)
                            st.session_state.last_sync_status = f"⚠️ Offline: {message}"
                            # Still store in history
                            st.session_state.sales_history.insert(0, {**data, 'status': 'pending'})
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="spar-card-green">', unsafe_allow_html=True)
        st.markdown("### 📊 Connection Status")
        
        # Retry offline queue button
        if st.session_state.offline_queue:
            if st.button("🔄 Retry Pending Sales", use_container_width=True):
                successful = []
                failed = []
                
                for data in st.session_state.offline_queue:
                    success, _ = send_to_webhook(data)
                    if success:
                        successful.append(data)
                    else:
                        failed.append(data)
                
                st.session_state.offline_queue = failed
                if successful:
                    st.success(f"✅ {len(successful)} sales synced to ETL!")
                if failed:
                    st.warning(f"⚠️ {len(failed)} sales still pending")
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📈 Today's Summary")
        
        # Show current session stats
        if st.session_state.sales_history:
            df_session = pd.DataFrame(st.session_state.sales_history)
            if not df_session.empty and 'total_sales' in df_session.columns:
                st.metric("This Session", f"${df_session['total_sales'].sum():,.2f}")
                st.metric("Transactions", len(df_session))
                if len(df_session) > 0:
                    st.metric("Avg Order", f"${df_session['total_sales'].mean():,.2f}")
        
        st.markdown("---")
        st.markdown("### ℹ️ How It Works")
        st.markdown("""
        1. **Enter sale data** → Record is saved
        2. **Sent to your local ETL** via secure tunnel
        3. **Data saved to your raw_data folder**
        4. **Your ETL processes** as usual
        
        **If offline:** Data is queued and will sync automatically
        """)
        
        st.markdown("---")
        st.markdown("### 🔗 Current Webhook URL")
        st.code(WEBHOOK_URL, language="text")
        
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# TAB 2: SPAR REWARDS (unchanged - works with uploaded files)
# -----------------------------
with tab2:
    st.markdown('<div class="spar-card">', unsafe_allow_html=True)
    st.title("🏆 SPAR Rewards Analysis")
    st.markdown("Upload your SPAR rewards CSV file to analyze customer behavior and get insights")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="upload-box">', unsafe_allow_html=True)
        st.markdown("### 📁 Upload Rewards Data")
        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type=['csv'],
            help="Upload the SPAR Rewards CSV file"
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_filename = uploaded_file.name
            st.success(f"✅ File loaded: {uploaded_file.name}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📋 File Requirements")
        st.markdown("""
        Your CSV file should contain:
        - **CustomerID**
        - **Transaction Date**
        - **ReceiptNumber**
        - **SalesAmount**
        - **RewardsEarned**
        - **RewardsRedeemed**
        """)
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            st.markdown("---")
            st.markdown("### 📊 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            required_columns = ['CustomerID', 'Transaction Date', 'ReceiptNumber', 'SalesAmount', 'RewardsEarned', 'RewardsRedeemed']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"❌ Missing columns: {', '.join(missing_columns)}")
            else:
                st.success("✅ Processing analysis...")
                
                with st.spinner("Analyzing SPAR rewards data..."):
                    results_df = process_rewards_analysis(df)
                    st.session_state.rewards_results = results_df
                
                st.markdown("---")
                st.markdown("### 📈 Analysis Results")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Customers", len(results_df))
                with col2:
                    st.metric("Avg RFM Score", f"{results_df['RFM_Score'].mean():.1f}/15")
                with col3:
                    st.metric("Avg Churn Risk", f"{results_df['ChurnRisk'].mean():.1f}%")
                with col4:
                    st.metric("Total Rewards", f"{results_df['RewardsEarned'].sum():,.0f}")
                
                st.markdown("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Customer Segments")
                    segment_counts = results_df['Segment'].value_counts()
                    fig = px.pie(values=segment_counts.values, names=segment_counts.index,
                                title="SPAR Customer Segments",
                                color_discrete_sequence=[SPAR_RED, SPAR_GREEN, '#FF6B6B', '#4ECDC4', '#45B7D1'])
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("Churn Risk Distribution")
                    fig = px.histogram(results_df, x='ChurnRisk', nbins=20,
                                      title="Churn Risk Distribution",
                                      color_discrete_sequence=[SPAR_RED])
                    st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                st.subheader("🏅 Top Customers")
                top_customers = results_df.nlargest(10, 'Monetary')[['CustomerID', 'Monetary', 'Frequency', 'Segment', 'RecommendedAction']]
                st.dataframe(top_customers, use_container_width=True, hide_index=True)
                
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results (CSV)",
                    data=csv,
                    file_name=f"spar_rewards_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    else:
        st.info("👆 Upload a CSV file to begin analysis")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# TAB 3: DASHBOARD
# -----------------------------
with tab3:
    st.markdown('<div class="spar-card">', unsafe_allow_html=True)
    st.title("📈 Sales Dashboard")
    
    if st.session_state.sales_history:
        df_sales = pd.DataFrame(st.session_state.sales_history)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Sales", f"${df_sales['total_sales'].sum():,.2f}")
        with col2:
            st.metric("Transactions", len(df_sales))
        with col3:
            st.metric("Average Order", f"${df_sales['total_sales'].mean():,.2f}")
        with col4:
            st.metric("Total Rewards", f"{df_sales['rewards_earned'].sum():,.0f}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sales by Product")
            product_sales = df_sales.groupby('product')['total_sales'].sum().reset_index()
            fig = px.bar(product_sales, x='product', y='total_sales',
                        title="Sales by Product",
                        color_discrete_sequence=[SPAR_GREEN])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Recent Transactions")
            recent = df_sales.head(10)[['sale_id', 'customer_name', 'product', 'total_sales']]
            st.dataframe(recent, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df_sales.to_csv(index=False)
        st.download_button(
            label="📥 Download Session Data (CSV)",
            data=csv,
            file_name=f"spar_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No sales recorded in this session")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# TAB 4: SETTINGS
# -----------------------------
with tab4:
    st.markdown('<div class="spar-card">', unsafe_allow_html=True)
    st.title("⚙️ System Settings")
    
    st.subheader("🔗 Webhook Configuration")
    st.text_input("Webhook URL", value=WEBHOOK_URL, disabled=True)
    st.caption("Update this URL in the code if your tunnel URL changes")
    
    st.divider()
    
    st.subheader("📊 Session Data")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Sales in session:** {len(st.session_state.sales_history)}")
        st.write(f"**Pending sync:** {len(st.session_state.offline_queue)}")
    
    with col2:
        if st.button("🗑️ Clear Session Data", type="secondary"):
            st.session_state.sales_history = []
            st.session_state.offline_queue = []
            st.success("Session data cleared!")
            st.rerun()
    
    st.divider()
    
    st.subheader("ℹ️ System Information")
    st.write(f"**App Version:** 2.0 (Cloud-Ready)")
    st.write(f"**Deployment:** Streamlit Cloud")
    st.write(f"**Data Storage:** Webhook to local ETL")
    st.write(f"**Offline Queue:** {len(st.session_state.offline_queue)} pending records")
    
    st.divider()
    
    if st.button("🔌 Test Connection", use_container_width=True):
        is_connected = check_connection()
        if is_connected:
            st.success("✅ Connected to ETL server successfully!")
        else:
            st.error("❌ Cannot connect to ETL server")
            st.info(f"Make sure your tunnel is running at: {WEBHOOK_URL.replace('/webhook', '')}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# AUTO-RETRY OFFLINE QUEUE
# -----------------------------
if st.session_state.offline_queue and check_connection():
    # Try to sync offline queue
    successful = []
    for data in st.session_state.offline_queue[:5]:  # Process 5 at a time
        success, _ = send_to_webhook(data)
        if success:
            successful.append(data)
    
    for data in successful:
        st.session_state.offline_queue.remove(data)
    
    if successful:
        st.toast(f"✅ Synced {len(successful)} pending sales!", icon="✅")
        st.rerun()

# -----------------------------
# FOOTER
# -----------------------------
st.markdown(f"""
<div class="spar-footer">
    <p>🛒 SPAR Sales & Rewards Management System | Cloud-Powered with Local ETL Sync</p>
    <p style="font-size: 0.75rem;">© 2025 SPAR Group - Fresh. Fast. Friendly.</p>
</div>
""", unsafe_allow_html=True)