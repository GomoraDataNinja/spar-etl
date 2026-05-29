3. Replace the URL with your actual Cloudflare tunnel URL
4. Click **Save**
""")
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
# DATABASE QUERY FUNCTIONS
# ============================================

def check_connection():
"""Check if ETL server is reachable"""
try:
    health_url = WEBHOOK_URL.replace('/webhook', '/health')
    response = requests.get(health_url, timeout=5)
    return response.status_code == 200
except:
    return False

def get_sales_from_db(operator_name=None, date_filter=None, start_date=None, end_date=None):
"""Fetch sales from SQL Server via Flask receiver"""
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
    msg['Subject'] = f"NEW SALE - {sale_id}"
    
    recorded_by = st.session_state.current_user['name'] if st.session_state.current_user else 'Unknown'
    
    formatted_total = f"${total_sales:,.2f}"
    formatted_rewards = f"{rewards_earned:.0f}"
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #E3000F;">New SPAR Sale Recorded!</h2>
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
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown('<div class="app-name">Tengai</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; margin-bottom: 2rem;">SPAR Sales & Rewards System</p>', unsafe_allow_html=True)
    
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
    
    st.markdown('<p style="text-align: center; font-size: 0.7rem; margin-top: 1rem;">Contact your administrator to get an account</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# OPERATOR VIEW
# ============================================
def operator_view():
user_name = st.session_state.current_user['name']

st.markdown("""
<div class="app-header">
    <h1>Tengai - SPAR Sales System</h1>
    <p>Sales tracking • Customer management • Real-time recording</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col3:
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; gap: 0.5rem;">
        <div class="user-info" style="background: {SPAR_GREEN};">
            TILL OPERATOR
        </div>
        <div class="user-info">
            Hello {user_name}
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Sign Out", key="signout"):
        logout_user()
        st.rerun()

tab1, tab2 = st.tabs(["Record Sale", "My Sales Today"])

# TAB 1: Record Sale
with tab1:
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### New Purchase")
        
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
            st.markdown("#### Purchase Details")
            
            col_e, col_f = st.columns(2)
            with col_e:
                product = st.selectbox("Product Category", [
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
            st.info(f"Rewards Points Earned: {rewards_earned:.0f} (2% of purchase)")
            
            submitted = st.form_submit_button("Record Sale", use_container_width=True)
            
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
                    st.success(f"Sale recorded! ID: {sale_id}")
                    st.balloons()
                else:
                    st.warning(f"Sale recorded but not sent to ETL: {message}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### Today's Stats")
        
        if check_connection():
            today_sales = get_sales_from_db(operator_name=user_name, date_filter='today')
            if today_sales:
                df_today = pd.DataFrame(today_sales)
                total_revenue = df_today['total_sales'].sum() if 'total_sales' in df_today.columns else 0
                st.metric("Today's Revenue", f"${total_revenue:,.2f}")
                st.metric("Today's Transactions", len(df_today))
            else:
                st.info("No sales recorded yet today")
            st.success("ETL Connected")
        else:
            st.warning("ETL Offline - Tunnel may be down")
        
        st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: My Sales Today
with tab2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown(f"### My Sales Today - {user_name}")
    
    if check_connection():
        today_sales = get_sales_from_db(operator_name=user_name, date_filter='today')
        
        if today_sales:
            df = pd.DataFrame(today_sales)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Transactions", len(df))
            with col2:
                total_revenue = df['total_sales'].sum() if 'total_sales' in df.columns else 0
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
            with col3:
                avg_sale = df['total_sales'].mean() if 'total_sales' in df.columns else 0
                st.metric("Average Sale", f"${avg_sale:.2f}")
            with col4:
                customers = df['customer_name'].nunique() if 'customer_name' in df.columns else 0
                st.metric("Customers Served", customers)
            
            st.markdown("#### Your Sales Today")
            display_cols = ['sale_id', 'customer_name', 'product_category', 'quantity', 'total_sales', 'sale_time']
            available_cols = [c for c in display_cols if c in df.columns]
            if available_cols:
                st.dataframe(df[available_cols], use_container_width=True, height=400)
            else:
                st.info("No data to display")
        else:
            st.info("No sales recorded today. Start selling!")
    else:
        st.warning("Cannot connect to ETL server. Please check your tunnel connection.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# ADMIN VIEW
# ============================================
def admin_view():
user_name = st.session_state.current_user['name']

st.markdown("""
<div class="app-header">
    <h1>Tengai - SPAR Sales & Rewards System</h1>
    <p>Sales tracking • Rewards intelligence • Customer retention</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col3:
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; gap: 0.5rem;">
        <div class="user-info" style="background: {SPAR_RED};">
            ADMIN
        </div>
        <div class="user-info">
            Hello {user_name}
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Sign Out", key="signout"):
        logout_user()
        st.rerun()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Record Sale", "Today's Sales", "Sales Reports", "Rewards Analysis", "Admin Panel"
])

# TAB 1: Record Sale
with tab1:
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### New Purchase")
        
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
            st.markdown("#### Purchase Details")
            
            col_e, col_f = st.columns(2)
            with col_e:
                product = st.selectbox("Product Category", [
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
            st.info(f"Rewards Points Earned: {rewards_earned:.0f} (2% of purchase)")
            
            submitted = st.form_submit_button("Record Sale", use_container_width=True)
            
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
                    st.success(f"Sale recorded! ID: {sale_id}")
                    st.balloons()
                else:
                    st.warning(f"Sale recorded but not sent to ETL: {message}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("### System Status")
        
        if check_connection():
            st.success("ETL Connected")
            st.info("Data is being sent to SQL Server")
        else:
            st.warning("ETL Offline - Tunnel may be down")
            st.info("Update your WEBHOOK_URL in Settings -> Secrets")
        
        st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: Today's All Sales
with tab2:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### Today's All Sales (All Operators)")
    
    if check_connection():
        today_sales = get_sales_from_db(date_filter='today')
        
        if today_sales:
            df = pd.DataFrame(today_sales)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Transactions", len(df))
            with col2:
                total_revenue = df['total_sales'].sum() if 'total_sales' in df.columns else 0
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
            with col3:
                avg_sale = df['total_sales'].mean() if 'total_sales' in df.columns else 0
                st.metric("Average Sale", f"${avg_sale:.2f}")
            with col4:
                operators = df['recorded_by'].nunique() if 'recorded_by' in df.columns else 0
                st.metric("Active Operators", operators)
            
            st.markdown("#### Today's Sales Details")
            display_cols = ['sale_id', 'recorded_by', 'customer_name', 'product_category', 'quantity', 'total_sales', 'sale_time']
            available_cols = [c for c in display_cols if c in df.columns]
            if available_cols:
                st.dataframe(df[available_cols], use_container_width=True, height=400)
            
            if 'recorded_by' in df.columns and 'total_sales' in df.columns:
                st.markdown("#### Operator Performance Today")
                operator_today = df.groupby('recorded_by').agg({
                    'sale_id': 'count',
                    'total_sales': 'sum'
                }).rename(columns={'sale_id': 'Transactions', 'total_sales': 'Revenue'}).reset_index()
                operator_today['Revenue'] = operator_today['Revenue'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(operator_today, use_container_width=True)
        else:
            st.info("No sales recorded today")
    else:
        st.warning("ETL Server not connected")
    
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: Sales Reports
with tab3:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### Sales Reports & Analytics")
    
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
                st.markdown("#### Daily Sales Trend")
                df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
                daily_sales = df.groupby('sale_date')['total_sales'].sum().reset_index()
                fig = px.line(daily_sales, x='sale_date', y='total_sales', 
                              title="Sales Over Time", markers=True,
                              color_discrete_sequence=[SPAR_GREEN])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            if 'recorded_by' in df.columns:
                st.markdown("#### Operator Performance")
                operator_perf = df.groupby('recorded_by').agg({
                    'sale_id': 'count',
                    'total_sales': 'sum'
                }).rename(columns={'sale_id': 'Transactions', 'total_sales': 'Revenue'}).reset_index()
                operator_perf['Revenue'] = operator_perf['Revenue'].apply(lambda x: f"${x:,.2f}")
                st.dataframe(operator_perf, use_container_width=True)
            
            st.markdown("---")
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Full Report (CSV)",
                data=csv,
                file_name=f"spar_sales_report_{start_date}_to_{end_date}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info(f"No sales found between {start_date} and {end_date}")
    else:
        st.warning("Cannot connect to ETL server")
    
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 4: Rewards Analysis
with tab4:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### Rewards Intelligence Hub")
    st.markdown("Upload your customer transaction data to unlock powerful insights")
    
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'], key="rewards_upload")
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df = clean_rewards_data(df)
        
        if not df.empty:
            st.success(f"Loaded {len(df)} transactions from {df['member_number'].nunique()} unique customers")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Revenue", safe_currency_format(df['basket_value'].sum()))
            with col2:
                st.metric("Total Transactions", f"{len(df):,}")
            with col3:
                st.metric("Unique Customers", f"{df['member_number'].nunique():,}")
            with col4:
                st.metric("Avg Basket", safe_currency_format(df['basket_value'].mean()))
            
            rfm = calculate_rfm(df)
            rfm = segment_customers(rfm)
            rfm = calculate_clv(rfm)
            rfm = calculate_churn_probability(rfm)
            rfm = generate_actions(rfm)
            rfm = rfm.reset_index()
            
            seg_counts = rfm['segment'].value_counts().reset_index()
            seg_counts.columns = ['Segment', 'Count']
            fig = px.pie(seg_counts, values='Count', names='Segment', 
                         color_discrete_sequence=[SPAR_GREEN, SPAR_RED, '#FFA07A', '#D3D3D3', '#90EE90'],
                         hole=0.3)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### High Priority Customers (At Risk / Warming)")
            high_priority = rfm[rfm['priority'] == 'High'].head(10)
            if not high_priority.empty:
                display_cols = ['member_number', 'segment', 'recency', 'frequency', 'monetary', 'churn_risk', 'recommended_action']
                st.dataframe(high_priority[display_cols], use_container_width=True)
        else:
            st.error("No valid data found")
    else:
        st.info("Please upload a CSV file with columns: member_number, redemption_date, basket_value (or amount)")
    
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 5: Admin Panel
with tab5:
    st.markdown('<div class="content-card">', unsafe_allow_html=True)
    st.markdown("### Admin Control Panel")
    
    st.markdown("#### Create New Operator Account")
    
    with st.form("create_operator_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name *", placeholder="Operator's full name")
            new_username = st.text_input("Username *", placeholder="operator_username")
        with col2:
            new_email = st.text_input("Email *", placeholder="operator@store.com")
            new_password = st.text_input("Password *", type="password", placeholder="Min 6 characters")
        
        submitted = st.form_submit_button("Create Operator", use_container_width=True)
        
        if submitted:
            if not all([new_name, new_username, new_email, new_password]):
                st.error("Please fill all fields")
            elif len(new_password) < 6:
                st.error("Password must be at least 6 characters")
            else:
                success, message = register_user(new_name, new_username, new_email, new_password, role="user")
                if success:
                    st.success(f"{message}")
                    st.info(f"Operator can login with username: {new_username}")
                else:
                    st.error(f"{message}")
    
    st.divider()
    st.markdown("#### Existing Users")
    
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
    
    st.divider()
    st.markdown("#### System Status")
    
    if check_connection():
        st.success("ETL Server Connected")
        st.success("Database Connection Active")
    else:
        st.error("ETL Server Offline")
        st.info("""
        **To fix this:**
        1. Make sure your local Flask receiver is running
        2. Make sure Cloudflare tunnel is active
        3. Update the WEBHOOK_URL in Settings -> Secrets
        """)
    
    st.divider()
    st.markdown("#### Current Configuration")
    st.code(f"WEBHOOK_URL = {WEBHOOK_URL}", language="python")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN
# ============================================
if st.session_state.logged_in:
user_role = st.session_state.current_user.get('role', 'user')
if user_role == 'admin':
    admin_view()
else:
    operator_view()
else:
login_screen()
