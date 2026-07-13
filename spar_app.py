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
    page_title="Tengai - SPAR Sales & Rewards",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# PRODUCT DATA - SPAR PRODUCTS BY CATEGORY
# ============================================
SPAR_PRODUCTS = {
    "Fresh Produce": [
        "Apples - Golden Delicious", "Apples - Granny Smith", "Bananas - Fresh",
        "Oranges - Navel", "Avocados - Hass", "Tomatoes - Vine Ripened",
        "Potatoes - White", "Onions - Brown", "Carrots - Fresh", "Lettuce - Iceberg",
        "Broccoli - Fresh", "Cauliflower - Fresh", "Spinach - Baby Leaves",
        "Strawberries - Fresh", "Grapes - Red Seedless", "Lemons - Fresh",
        "Limes - Fresh", "Mangoes - Fresh", "Pineapples - Whole", "Watermelon - Fresh Cut"
    ],
    "Meat and Poultry": [
        "Beef - Steak (Rump)", "Beef - Mince (Lean)", "Chicken - Whole",
        "Chicken - Breast Fillets", "Chicken - Thighs", "Pork - Chops",
        "Pork - Ribs", "Lamb - Chops", "Lamb - Leg Roast", "Boerewors - Classic",
        "Sausages - Pork", "Bacon - Streaky", "Ham - Sliced", "Turkey - Breast", "Droëwors - Original"
    ],
    "Dairy": [
        "Milk - Fresh Full Cream", "Milk - Low Fat", "Milk - Lactose Free",
        "Cheddar Cheese - Block", "Gouda Cheese - Block", "Cream Cheese - Plain",
        "Butter - Salted", "Yogurt - Plain", "Yogurt - Greek Style", "Sour Cream",
        "Cream - Fresh", "Cottage Cheese", "Mozzarella Cheese", "Feta Cheese", "Long Life Milk"
    ],
    "Bakery": [
        "Brown Bread - Fresh", "White Bread - Fresh", "Whole Wheat Bread",
        "Rolls - Sesame", "Croissants - Butter", "Muffins - Blueberry",
        "Muffins - Chocolate Chip", "Cupcakes - Vanilla", "Doughnuts - Glazed",
        "Pies - Steak", "Pies - Chicken", "Scones - Plain", "Baguette - Fresh",
        "Ciabatta - Fresh", "Rye Bread"
    ],
    "Beverages": [
        "Coca Cola - 2L", "Coca Cola - Can", "Fanta Orange - 2L", "Sprite - 2L",
        "Water - Still 500ml", "Water - Sparkling", "Juice - Orange", "Juice - Apple",
        "Juice - Mixed Fruit", "Coffee - Instant", "Tea - Rooibos", "Tea - English Breakfast",
        "Energy Drink - Red Bull", "Iced Tea - Lemon"
    ],
    "Household": [
        "Toilet Paper - 12 Pack", "Paper Towels - 3 Pack", "Dishwashing Liquid",
        "Laundry Detergent - 2kg", "Fabric Softener", "All Purpose Cleaner",
        "Bathroom Cleaner", "Glass Cleaner", "Garbage Bags - Large", "Sponges - Pack of 4",
        "Rubber Gloves", "Mop Refill", "Broom - Household"
    ],
    "Personal Care": [
        "Shampoo - Regular", "Conditioner - Regular", "Body Wash - Fragrance",
        "Soap - Bar", "Deodorant - Roll On", "Toothpaste - 100ml", "Toothbrush - Soft",
        "Facial Cleanser", "Moisturizer - Face", "Sunscreen - SPF 30", "Hair Gel",
        "Razor - Disposable", "Shaving Cream", "Cotton Balls - 100 Pack", "Tissues - Pocket Pack"
    ]
}

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
        background: #f5f7fa;
    }
    
    .login-card-tight {
        background: white;
        border-radius: 16px;
        padding: 2rem 2rem 1.5rem 2rem;
        max-width: 380px;
        width: 100%;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #e8eaed;
        text-align: center;
    }
    
    .app-name-tight {
        font-size: 1.75rem;
        font-weight: 600;
        color: #5e9bff;
        margin-bottom: 0.25rem;
    }
    
    .signin-text-tight {
        font-size: 0.8rem;
        color: #5f6368;
        margin-bottom: 0.25rem;
    }
    
    .version-info-tight {
        font-size: 0.65rem;
        color: #9aa0a6;
        margin-bottom: 1.25rem;
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
        font-weight: 700 !important;
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
        color: #5e9bff !important;
    }
    
    div[data-testid="stMetric"] label {
        color: #5f6368 !important;
        font-size: 0.7rem !important;
    }
    
    div[data-testid="stMetric"] div {
        color: #5e9bff !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
    }
    
    .stButton > button {
        background: #5e9bff !important;
        color: white !important;
        border: none;
        border-radius: 24px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        font-size: 0.8rem;
    }
    
    .stButton > button:hover {
        background: #4a7fd4 !important;
    }
    
    .modern-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
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
        background: linear-gradient(135deg, #5e9bff 0%, #7aadff 100%);
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
        color: #5e9bff;
    }
    
    .role-badge {
        background: #5e9bff;
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
        background: #5e9bff;
        color: white;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    div[data-testid="stTextInput"]:first-of-type label {
        display: none !important;
    }
    
    .metric-modern {
        background: white;
        border-radius: 12px;
        padding: 0.75rem;
        text-align: center;
        border: 1px solid #e8eaed;
    }
    
    .metric-value-modern {
        font-size: 1.25rem;
        font-weight: 600;
        color: #5e9bff;
        margin-bottom: 0.25rem;
    }
    
    .metric-label-modern {
        font-size: 0.6rem;
        color: #5f6368;
        font-weight: 500;
        text-transform: uppercase;
    }
    
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
            <div class="app-name-tight">Configuration Required</div>
            <div class="signin-text-tight">Please set up your Cloudflare tunnel URL</div>
            <div style="background: #f1f5f9; padding: 0.75rem; border-radius: 8px; text-align: left; margin-top: 0.75rem; font-size: 0.7rem;">
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
            <h2 style="color: #5e9bff;">New SPAR Sale Recorded!</h2>
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
# LOGIN SCREEN
# ============================================
def login_screen():
    st.markdown("""
    <div class="login-centered">
        <div class="login-card-tight">
            <div class="app-name-tight">Tengai</div>
            <div class="signin-text-tight">Sign in to continue</div>
            <div class="version-info-tight">Version 3.5.0 - Production</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("Sign In", use_container_width=False)
        
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
                st.warning("Please enter your username and password")
    
    st.markdown("""
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
    
    st.markdown(f"""
    <div class="nav-bar">
        <div class="logo-area">
            <span style="font-size: 1rem;">🛒</span>
            <span class="logo-text">Tengai</span>
        </div>
        <div class="user-area">
            <span class="role-badge">{user_role.upper()}</span>
            <span class="user-name-badge">{user_name}</span>
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
# OPERATOR VIEW - WITH REAL-TIME PRODUCT UPDATES
# ============================================
def operator_view():
    user_name = st.session_state.current_user['name']
    
    # Initialize counter for form reset if not exists
    if 'op_form_counter' not in st.session_state:
        st.session_state.op_form_counter = 0
    
    tab1, tab2 = st.tabs(["📝 Record Sale", "📊 My Sales Today"])
    
    with tab1:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📋 New Purchase</div>', unsafe_allow_html=True)
            
            # Customer Details
            col_a, col_b = st.columns(2)
            with col_a:
                customer_name = st.text_input("Customer Name *", placeholder="Enter full name", key=f"op_name_{st.session_state.op_form_counter}")
            with col_b:
                customer_email = st.text_input("Email Address", placeholder="customer@example.com", key=f"op_email_{st.session_state.op_form_counter}")
            
            col_c, col_d = st.columns(2)
            with col_c:
                customer_id = st.text_input("SPAR Rewards ID", placeholder="Optional", key=f"op_cid_{st.session_state.op_form_counter}")
            with col_d:
                phone = st.text_input("Phone Number", placeholder="Optional", key=f"op_phone_{st.session_state.op_form_counter}")
            
            st.markdown("---")
            st.markdown('<p style="color: #202124; font-weight: 600;">🛍️ Purchase Details</p>', unsafe_allow_html=True)
            
            # Product Category
            product_category = st.selectbox(
                "Product Category", 
                list(SPAR_PRODUCTS.keys()),
                key=f"op_category_{st.session_state.op_form_counter}"
            )
            
            # Product
            products = SPAR_PRODUCTS.get(product_category, [])
            product = st.selectbox(
                "Product", 
                products,
                key=f"op_product_{st.session_state.op_form_counter}"
            )
            
            col_e, col_f = st.columns(2)
            with col_e:
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key=f"op_qty_{st.session_state.op_form_counter}")
            with col_f:
                unit_price = st.number_input("Unit Price (USD)", min_value=0.01, value=0.01, step=0.01, format="%.2f", key=f"op_price_{st.session_state.op_form_counter}")
            
            total_sales = quantity * unit_price
            st.metric("Total Amount", f"${total_sales:,.2f}")
            st.caption(f"📅 Purchased Date: {datetime.now().strftime('%m/%d/%Y')}")
            
            rewards_earned = total_sales * 0.02
            st.info(f"⭐ Rewards Points Earned: {rewards_earned:.0f} (2% of purchase)")
            
            submitted = st.button("💾 Record Sale", key=f"op_submit_{st.session_state.op_form_counter}", use_container_width=True)
            
            if submitted:
                if not customer_name:
                    st.error("Please enter customer name")
                else:
                    now = datetime.now()
                    sale_id = generate_sale_id()
                    total_sales_calc = quantity * unit_price
                    rewards_earned_calc = total_sales_calc * 0.02
                    
                    data = {
                        'sale_id': sale_id,
                        'customer_name': customer_name,
                        'customer_email': customer_email,
                        'customer_id': customer_id if customer_id else None,
                        'phone': phone if phone else None,
                        'product_category': product_category,
                        'product': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_sales': total_sales_calc,
                        'rewards_earned': rewards_earned_calc,
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
                    send_admin_notification(customer_name, sale_id, product, quantity, total_sales_calc, rewards_earned_calc, customer_email)
                    st.session_state.sales_history.insert(0, data)
                    
                    if success:
                        st.success(f"✅ Sale recorded! ID: {sale_id}")
                        st.balloons()
                        st.session_state.op_form_counter += 1
                        st.rerun()
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
                    st.metric("Today's Revenue", f"${total_revenue:,.2f}")
                    st.metric("Today's Transactions", len(df_today))
                else:
                    st.info("No sales recorded yet today")
            else:
                st.warning("⚠️ ETL Offline - Tunnel may be down")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown(f'<div class="card-header">📊 My Sales Today - {user_name}</div>', unsafe_allow_html=True)
        
        if check_connection():
            today_sales = get_sales_from_db(operator_name=user_name, date_filter='today')
            
            if today_sales:
                df = pd.DataFrame(today_sales)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Transactions", len(df))
                with col2:
                    total_revenue = df['total_sales'].sum() if 'total_sales' in df.columns else 0
                    st.metric("Revenue", f"${total_revenue:,.2f}")
                with col3:
                    avg_sale = df['total_sales'].mean() if 'total_sales' in df.columns else 0
                    st.metric("Average Sale", f"${avg_sale:.2f}")
                with col4:
                    customers = df['customer_name'].nunique() if 'customer_name' in df.columns else 0
                    st.metric("Customers Served", customers)
                
                st.markdown("#### Your Sales Today")
                display_cols = ['sale_id', 'customer_name', 'product', 'quantity', 'total_sales', 'sale_time']
                available_cols = [c for c in display_cols if c in df.columns]
                if available_cols:
                    st.dataframe(df[available_cols], use_container_width=True, height=300)
            else:
                st.info("No sales recorded today. Start selling!")
        else:
            st.warning("Cannot connect to ETL server")
        
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# ADMIN VIEW - WITH REAL-TIME PRODUCT UPDATES
# ============================================
def admin_view():
    user_name = st.session_state.current_user['name']
    
    # Initialize counter for form reset if not exists
    if 'admin_form_counter' not in st.session_state:
        st.session_state.admin_form_counter = 0
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Record Sale", "📊 Today's Sales", "📈 Sales Reports", "🏆 Rewards Analysis", "⚙️ Admin Panel"
    ])
    
    with tab1:
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-header">📋 New Purchase</div>', unsafe_allow_html=True)
            
            # Customer Details
            col_a, col_b = st.columns(2)
            with col_a:
                customer_name = st.text_input("Customer Name *", placeholder="Enter full name", key=f"admin_name_{st.session_state.admin_form_counter}")
            with col_b:
                customer_email = st.text_input("Email Address", placeholder="customer@example.com", key=f"admin_email_{st.session_state.admin_form_counter}")
            
            col_c, col_d = st.columns(2)
            with col_c:
                customer_id = st.text_input("SPAR Rewards ID", placeholder="Optional", key=f"admin_cid_{st.session_state.admin_form_counter}")
            with col_d:
                phone = st.text_input("Phone Number", placeholder="Optional", key=f"admin_phone_{st.session_state.admin_form_counter}")
            
            st.markdown("---")
            st.markdown('<p style="color: #202124; font-weight: 600;">🛍️ Purchase Details</p>', unsafe_allow_html=True)
            
            # Product Category
            product_category = st.selectbox(
                "Product Category", 
                list(SPAR_PRODUCTS.keys()),
                key=f"admin_category_{st.session_state.admin_form_counter}"
            )
            
            # Product
            products = SPAR_PRODUCTS.get(product_category, [])
            product = st.selectbox(
                "Product", 
                products,
                key=f"admin_product_{st.session_state.admin_form_counter}"
            )
            
            col_e, col_f = st.columns(2)
            with col_e:
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key=f"admin_qty_{st.session_state.admin_form_counter}")
            with col_f:
                unit_price = st.number_input("Unit Price (USD)", min_value=0.01, value=0.01, step=0.01, format="%.2f", key=f"admin_price_{st.session_state.admin_form_counter}")
            
            total_sales = quantity * unit_price
            st.metric("Total Amount", f"${total_sales:,.2f}")
            st.caption(f"📅 Purchased Date: {datetime.now().strftime('%m/%d/%Y')}")
            
            rewards_earned = total_sales * 0.02
            st.info(f"⭐ Rewards Points Earned: {rewards_earned:.0f} (2% of purchase)")
            
            submitted = st.button("💾 Record Sale", key=f"admin_submit_{st.session_state.admin_form_counter}", use_container_width=True)
            
            if submitted:
                if not customer_name:
                    st.error("Please enter customer name")
                else:
                    now = datetime.now()
                    sale_id = generate_sale_id()
                    total_sales_calc = quantity * unit_price
                    rewards_earned_calc = total_sales_calc * 0.02
                    
                    data = {
                        'sale_id': sale_id,
                        'customer_name': customer_name,
                        'customer_email': customer_email,
                        'customer_id': customer_id if customer_id else None,
                        'phone': phone if phone else None,
                        'product_category': product_category,
                        'product': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_sales': total_sales_calc,
                        'rewards_earned': rewards_earned_calc,
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
                    send_admin_notification(customer_name, sale_id, product, quantity, total_sales_calc, rewards_earned_calc, customer_email)
                    
                    if success:
                        st.success(f"✅ Sale recorded! ID: {sale_id}")
                        st.balloons()
                        st.session_state.admin_form_counter += 1
                        st.rerun()
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
    
    with tab2:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📊 Today\'s All Sales (All Operators)</div>', unsafe_allow_html=True)
        
        if check_connection():
            today_sales = get_sales_from_db(date_filter='today')
            
            if today_sales:
                df = pd.DataFrame(today_sales)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Transactions", len(df))
                with col2:
                    total_revenue = df['total_sales'].sum() if 'total_sales' in df.columns else 0
                    st.metric("Revenue", f"${total_revenue:,.2f}")
                with col3:
                    avg_sale = df['total_sales'].mean() if 'total_sales' in df.columns else 0
                    st.metric("Average Sale", f"${avg_sale:.2f}")
                with col4:
                    operators = df['recorded_by'].nunique() if 'recorded_by' in df.columns else 0
                    st.metric("Active Operators", operators)
                
                st.markdown("#### 📋 Today's Sales Details")
                display_cols = ['sale_id', 'recorded_by', 'customer_name', 'product', 'quantity', 'total_sales', 'sale_time']
                available_cols = [c for c in display_cols if c in df.columns]
                if available_cols:
                    st.dataframe(df[available_cols], use_container_width=True, height=300)
                
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
                    st.metric("Total Sales", f"${total_revenue:,.2f}")
                with col2:
                    st.metric("Transactions", len(df))
                with col3:
                    customers = df['customer_name'].nunique() if 'customer_name' in df.columns else 0
                    st.metric("Unique Customers", customers)
                with col4:
                    avg_sale = df['total_sales'].mean() if 'total_sales' in df.columns else 0
                    st.metric("Avg Transaction", f"${avg_sale:.2f}")
                
                if 'sale_date' in df.columns and 'total_sales' in df.columns:
                    st.markdown("#### 📅 Daily Sales Trend")
                    df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
                    daily_sales = df.groupby('sale_date')['total_sales'].sum().reset_index()
                    fig = px.line(daily_sales, x='sale_date', y='total_sales', 
                                  title="Sales Over Time", markers=True,
                                  color_discrete_sequence=['#5e9bff'])
                    fig.update_layout(height=350, plot_bgcolor='white', paper_bgcolor='white')
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
    
    with tab4:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">🏆 Rewards Intelligence Hub</div>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload CSV file", type=['csv'], key="rewards_upload")
        
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            df = clean_rewards_data(df)
            
            if not df.empty:
                st.success(f"Loaded {len(df)} transactions from {df['member_number'].nunique()} unique customers")
                
                rfm = calculate_rfm(df)
                rfm = segment_customers(rfm)
                rfm = calculate_clv(rfm)
                rfm = calculate_churn_probability(rfm)
                rfm = generate_actions(rfm)
                rfm = rfm.reset_index()
                
                seg_counts = rfm['segment'].value_counts().reset_index()
                seg_counts.columns = ['Segment', 'Count']
                fig = px.pie(seg_counts, values='Count', names='Segment', 
                             color_discrete_sequence=['#5e9bff', '#f59e0b', '#ef4444', '#10b981', '#8b5cf6'],
                             hole=0.3)
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("No valid data found")
        else:
            st.info("Upload a CSV file with columns: member_number, redemption_date, basket_value")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">⚙️ Admin Control Panel</div>', unsafe_allow_html=True)
        
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
                        st.success(f"{message}")
                    else:
                        st.error(f"{message}")
        
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
            st.success("ETL Server Connected")
        else:
            st.error("ETL Server Offline")
        
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
