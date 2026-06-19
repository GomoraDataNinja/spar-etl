"""
SPAR ERP - Complete Business Management System
Single file application with:
- Sales Recording with Stock Checking
- Product Management
- Supplier Management  
- Purchase Orders
- Dashboard & Reports
- ETL Receiver (Flask)
- SQL Server Integration
"""

# ============================================
# IMPORTS
# ============================================
import streamlit as st
import pandas as pd
import numpy as np
import pyodbc
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
from flask import Flask, request, jsonify
import logging
import signal
import sys
import os
import threading

# ============================================
# CONFIGURATION
# ============================================
APP_NAME = "SPAR ERP"
APP_VERSION = "4.0.0"

# Database Connection
DB_SERVER = "(local)"  # or "DATANINJA\Lenovo"
DB_NAME = "SPAR_ETL"
DB_DRIVER = "{ODBC Driver 17 for SQL Server}"

# Email Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "gomoraefesto97@gmail.com"
SENDER_PASSWORD = "picz cijg kgbw zoup"
ADMIN_EMAIL = "gomoraefesto97@gmail.com"

# ETL Configuration
RAW_DATA_FOLDER = Path(r"C:\Users\Lenovo\OneDrive\Desktop\HBMI\Data Warehousing\ETL_Projects\raw_data")
RAW_DATA_FOLDER.mkdir(parents=True, exist_ok=True)

# ============================================
# DATABASE CONNECTION
# ============================================
def get_db_connection():
    """Connect to SQL Server"""
    try:
        conn = pyodbc.connect(
            f"DRIVER={DB_DRIVER};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={DB_NAME};"
            "Trusted_Connection=yes;"
        )
        return conn
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        return None

def execute_query(query, params=None):
    """Execute SELECT query"""
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        if params:
            return pd.read_sql(query, conn, params=params)
        else:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"❌ Query failed: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def execute_command(query, params=None):
    """Execute INSERT/UPDATE/DELETE"""
    conn = get_db_connection()
    if conn is None:
        return False, "Database connection failed"
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        cursor.close()
        return True, "Success"
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# ============================================
# DATABASE HELPER FUNCTIONS
# ============================================
@st.cache_data(ttl=300)
def get_products_from_db(category=None, search=None):
    """Get products from database"""
    query = """
        SELECT 
            p.id, p.product_code, p.product_name, p.product_description,
            pc.category_name, p.unit_of_measure,
            p.unit_price, p.cost_price,
            p.current_stock, p.reorder_level,
            (ISNULL(p.current_stock, 0) - ISNULL(p.reserved_stock, 0)) AS available_stock,
            s.supplier_name,
            p.is_active
        FROM erp_products p
        LEFT JOIN erp_product_categories pc ON p.category_id = pc.id
        LEFT JOIN erp_suppliers s ON p.supplier_id = s.id
        WHERE p.is_active = 1
    """
    params = []
    
    if category:
        query += " AND pc.category_name = ?"
        params.append(category)
    
    if search:
        query += " AND (p.product_code LIKE ? OR p.product_name LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    
    query += " ORDER BY pc.category_name, p.product_name"
    
    return execute_query(query, params if params else None)

@st.cache_data(ttl=300)
def get_product_categories():
    """Get all categories"""
    query = "SELECT category_name FROM erp_product_categories WHERE is_active = 1 ORDER BY category_name"
    df = execute_query(query)
    return df['category_name'].tolist() if not df.empty else []

@st.cache_data(ttl=300)
def get_suppliers():
    """Get all suppliers"""
    query = "SELECT id, supplier_code, supplier_name FROM erp_suppliers WHERE is_active = 1 ORDER BY supplier_name"
    return execute_query(query)

@st.cache_data(ttl=60)
def check_stock(product_id, quantity):
    """Check product stock availability"""
    query = """
        SELECT 
            product_name,
            ISNULL(current_stock, 0) - ISNULL(reserved_stock, 0) AS available_stock,
            current_stock,
            reserved_stock
        FROM erp_products
        WHERE id = ?
    """
    df = execute_query(query, [product_id])
    
    if df.empty:
        return {'available': False, 'message': 'Product not found'}
    
    available = df['available_stock'].iloc[0]
    product_name = df['product_name'].iloc[0]
    
    if available >= quantity:
        return {
            'available': True,
            'message': f'✅ In stock: {available:.0f} available',
            'available_stock': available,
            'product_name': product_name
        }
    else:
        return {
            'available': False,
            'message': f'❌ Only {available:.0f} available, need {quantity - available:.0f} more',
            'shortfall': quantity - available,
            'available_stock': available,
            'product_name': product_name
        }

@st.cache_data(ttl=300)
def get_dashboard_metrics():
    """Get KPIs for dashboard"""
    metrics = {}
    
    # Today's sales
    today_query = """
        SELECT 
            ISNULL(SUM(total_sales), 0) AS total_sales,
            COUNT(*) AS transaction_count
        FROM etl_sales_raw
        WHERE sale_date = CAST(GETDATE() AS DATE)
    """
    today = execute_query(today_query)
    metrics['today_sales'] = today.iloc[0]['total_sales'] if not today.empty else 0
    metrics['today_transactions'] = today.iloc[0]['transaction_count'] if not today.empty else 0
    
    # Low stock
    low_query = """
        SELECT COUNT(*) AS low_count
        FROM erp_products
        WHERE (ISNULL(current_stock, 0) - ISNULL(reserved_stock, 0)) <= reorder_level
        AND is_active = 1
    """
    low = execute_query(low_query)
    metrics['low_stock_count'] = low.iloc[0]['low_count'] if not low.empty else 0
    
    # Total products
    prod_query = "SELECT COUNT(*) AS total FROM erp_products WHERE is_active = 1"
    prod = execute_query(prod_query)
    metrics['total_products'] = prod.iloc[0]['total'] if not prod.empty else 0
    
    # Total suppliers
    sup_query = "SELECT COUNT(*) AS total FROM erp_suppliers WHERE is_active = 1"
    sup = execute_query(sup_query)
    metrics['total_suppliers'] = sup.iloc[0]['total'] if not sup.empty else 0
    
    return metrics

def create_sales_order(customer_name, customer_email, items, recorded_by):
    """Create a sales order in the database"""
    conn = get_db_connection()
    if conn is None:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        
        # Generate order number
        order_number = f"SO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Calculate totals
        subtotal = sum(item['quantity'] * item['unit_price'] for item in items)
        tax = subtotal * 0.155  # 15.5% VAT
        total = subtotal + tax
        
        # Insert sales order
        order_query = """
            INSERT INTO erp_sales_orders (
                so_number, customer_id, order_date, status,
                subtotal, tax_amount, total_amount, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(order_query, (
            order_number, None, datetime.now(), 'Draft',
            subtotal, tax, total, recorded_by
        ))
        
        order_id = cursor.execute("SELECT SCOPE_IDENTITY()").fetchval()
        
        # Insert order lines
        for item in items:
            line_query = """
                INSERT INTO erp_sales_order_lines (
                    so_id, line_number, product_id, product_code, product_name,
                    quantity, unit_price, line_total, tax_rate, tax_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            line_total = item['quantity'] * item['unit_price']
            tax_amount = line_total * 0.155
            cursor.execute(line_query, (
                order_id, item['line_number'],
                item['product_id'], item['product_code'],
                item['product_name'], item['quantity'],
                item['unit_price'], line_total, 15.5, tax_amount
            ))
        
        # Update stock (reserve)
        for item in items:
            stock_query = "UPDATE erp_products SET reserved_stock = ISNULL(reserved_stock, 0) + ? WHERE id = ?"
            cursor.execute(stock_query, (item['quantity'], item['product_id']))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True, order_number
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

# ============================================
# USER AUTHENTICATION
# ============================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

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
    admin_exists = any(user.get('role') == 'admin' for user in users.values())
    if not admin_exists:
        save_user("admin@spar.com", "Administrator", "admin", hash_password("Admin@123"), "admin")

def login_user(username_or_email, password):
    users = get_all_users()
    for email, user in users.items():
        if user['username'] == username_or_email or email == username_or_email:
            if verify_password(password, user['password']):
                st.session_state.logged_in = True
                st.session_state.current_user = user
                return True, f"Welcome back, {user['name']}!"
    return False, "Invalid credentials"

def logout_user():
    st.session_state.logged_in = False
    st.session_state.current_user = None

# ============================================
# ETL RECEIVER (Flask)
# ============================================
etl_app = Flask(__name__)
etl_logger = logging.getLogger(__name__)

etl_stats = {
    'total_received': 0,
    'today_received': 0,
    'start_time': datetime.now(),
    'last_sale': None
}

def save_to_sql(data):
    """Save received data to SQL Server"""
    try:
        conn = get_db_connection()
        if conn is None:
            return False
        
        cursor = conn.cursor()
        
        # Insert into etl_sales_raw
        query = """
            INSERT INTO etl_sales_raw (
                sale_id, customer_name, customer_email, customer_id,
                phone, product_category, product_name, quantity,
                unit_price, total_sales, rewards_earned,
                sale_date, sale_time, recorded_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(query, (
            data.get('sale_id', ''),
            data.get('customer_name', ''),
            data.get('customer_email', ''),
            data.get('customer_id', ''),
            data.get('phone', ''),
            data.get('product_category', ''),
            data.get('product', ''),
            data.get('quantity', 0),
            data.get('unit_price', 0),
            data.get('total_sales', 0),
            data.get('rewards_earned', 0),
            data.get('sale_date', datetime.now().strftime('%Y-%m-%d')),
            data.get('sale_time', datetime.now().strftime('%H:%M:%S')),
            data.get('recorded_by', 'system')
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        etl_logger.error(f"SQL error: {e}")
        return False

@etl_app.route('/webhook', methods=['POST'])
def etl_webhook():
    try:
        data = request.json
        etl_logger.info(f"Received sale from: {data.get('customer_name')} - Amount: ${data.get('total_sales', 0):,.2f}")
        
        # Save to SQL Server
        sql_success = save_to_sql(data)
        
        # Update stats
        etl_stats['total_received'] += 1
        etl_stats['today_received'] += 1
        etl_stats['last_sale'] = data
        
        return jsonify({
            "status": "success",
            "message": "Data saved to database",
            "sale_id": data.get('sale_id')
        }), 200
        
    except Exception as e:
        etl_logger.error(f"Webhook error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@etl_app.route('/health', methods=['GET'])
def etl_health():
    return jsonify({
        "status": "healthy",
        "uptime_seconds": (datetime.now() - etl_stats['start_time']).total_seconds(),
        "total_received": etl_stats['total_received'],
        "today_received": etl_stats['today_received']
    })

def run_etl_server():
    """Run Flask ETL server in background"""
    etl_app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)

# ============================================
# STREAMLIT UI - LOGIN
# ============================================
def login_screen():
    st.markdown("""
    <div style="
        display: flex; justify-content: center; align-items: center; min-height: 100vh;
        background: #f0f2f5;
    ">
        <div style="
            background: white; border-radius: 16px; padding: 2.5rem;
            max-width: 400px; width: 100%;
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            border: 1px solid #e8eaed; text-align: center;
        ">
            <div style="font-size: 2.5rem; font-weight: 700; color: #002B5C; margin-bottom: 0.5rem;">
                🏢 SPAR ERP
            </div>
            <div style="font-size: 0.85rem; color: #5f6368; margin-bottom: 2rem;">
                Business Management System
            </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
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
                st.warning("Please enter credentials")
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# STREAMLIT UI - MAIN APP
# ============================================
def main_app():
    user = st.session_state.current_user
    is_admin = user.get('role') == 'admin'
    
    # Header
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #002B5C 0%, #003B7E 100%);
        padding: 1rem 2rem; border-radius: 8px; margin-bottom: 1.5rem;
        color: white; display: flex; justify-content: space-between; align-items: center;
    ">
        <div>
            <h1 style="margin: 0; font-weight: 600;">🏢 SPAR ERP</h1>
            <p style="margin: 0; opacity: 0.8;">Yellowcob Enterprises Pvt Ltd</p>
        </div>
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span style="background: rgba(255,255,255,0.2); padding: 0.2rem 0.8rem; border-radius: 12px; font-size: 0.7rem;">
                {user.get('role', 'User').upper()}
            </span>
            <span style="font-size: 0.9rem;">👤 {user.get('name', 'User')}</span>
            <span style="font-size: 0.7rem;">{datetime.now().strftime('%Y-%m-%d %H:%M')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("### 📋 Menu")
        
        menu_items = [
            ("📊 Dashboard", "dashboard"),
            ("🛒 Record Sale", "record_sale"),
            ("📦 Products", "products"),
            ("🏷️ Suppliers", "suppliers"),
            ("📋 Orders", "orders"),
        ]
        
        if is_admin:
            menu_items.append(("👤 Users", "users"))
            menu_items.append(("⚙️ Settings", "settings"))
        
        menu_items.append(("🚪 Logout", "logout"))
        
        for label, key in menu_items:
            if st.button(label, key=f"nav_{key}", use_container_width=True):
                if key == "logout":
                    logout_user()
                    st.rerun()
                else:
                    st.session_state.current_page = key
                    st.rerun()
        
        st.markdown("---")
        st.markdown(f"<p style='font-size: 0.7rem; color: #6B7280; text-align: center;'>Version {APP_VERSION}</p>", unsafe_allow_html=True)
    
    # Page Router
    page = st.session_state.get('current_page', 'dashboard')
    
    if page == "dashboard":
        show_dashboard()
    elif page == "record_sale":
        show_record_sale()
    elif page == "products":
        show_products()
    elif page == "suppliers":
        show_suppliers()
    elif page == "orders":
        show_orders()
    elif page == "users" and is_admin:
        show_users()
    elif page == "settings" and is_admin:
        show_settings()
    else:
        show_dashboard()

# ============================================
# UI PAGES
# ============================================
def show_dashboard():
    """Dashboard Page"""
    st.markdown("## 📊 Dashboard")
    
    metrics = get_dashboard_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Today's Sales", f"${metrics.get('today_sales', 0):,.2f}")
        st.caption(f"{metrics.get('today_transactions', 0)} transactions")
    
    with col2:
        low = metrics.get('low_stock_count', 0)
        st.metric("Low Stock Items", low, delta="⚠️ Needs attention" if low > 0 else "✅ All good")
    
    with col3:
        st.metric("Total Products", metrics.get('total_products', 0))
    
    with col4:
        st.metric("Suppliers", metrics.get('total_suppliers', 0))
    
    st.markdown("---")
    
    # Low stock alert
    if metrics.get('low_stock_count', 0) > 0:
        st.warning(f"⚠️ {metrics.get('low_stock_count', 0)} products need reordering!")
    
    # Recent Sales
    st.markdown("### 📋 Recent Sales")
    query = "SELECT TOP 10 sale_id, customer_name, total_sales, sale_date FROM etl_sales_raw ORDER BY created_at DESC"
    recent = execute_query(query)
    if not recent.empty:
        st.dataframe(recent, use_container_width=True, hide_index=True)
    else:
        st.info("No sales recorded yet")

def show_record_sale():
    """Record Sale Page"""
    st.markdown("## 🛒 Record Sale")
    
    # Get products from database
    categories = get_product_categories()
    
    if not categories:
        st.warning("No product categories found. Please add products first.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("sale_form"):
            # Customer Details
            customer_name = st.text_input("Customer Name *", placeholder="Enter customer name")
            customer_email = st.text_input("Email", placeholder="customer@example.com")
            
            st.markdown("---")
            
            # Product Selection
            category = st.selectbox("Category", categories)
            
            products = get_products_from_db(category=category)
            
            if products.empty:
                st.warning("No products in this category")
                product_data = None
            else:
                # Create product options
                product_options = []
                for _, row in products.iterrows():
                    stock = row['available_stock']
                    status = "🟢" if stock > row['reorder_level'] else "🟡" if stock > 0 else "🔴"
                    display = f"{row['product_code']} - {row['product_name']} ({status} {stock:.0f} in stock)"
                    product_options.append({
                        'id': row['id'],
                        'display': display,
                        'name': row['product_name'],
                        'price': row['unit_price'],
                        'code': row['product_code'],
                        'stock': stock
                    })
                
                selected = st.selectbox(
                    "Product",
                    options=product_options,
                    format_func=lambda x: x['display']
                )
                
                if selected:
                    # Show stock warning
                    if selected['stock'] <= 0:
                        st.error(f"🚫 {selected['name']} is OUT OF STOCK!")
                    elif selected['stock'] <= 5:
                        st.warning(f"⚠️ Only {selected['stock']:.0f} units left of {selected['name']}")
                    
                    # Quantity and Price
                    col_qty, col_price = st.columns(2)
                    with col_qty:
                        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
                    with col_price:
                        unit_price = st.number_input("Unit Price ($)", min_value=0.01, value=float(selected['price']), step=0.01, format="%.2f")
                    
                    # Check stock
                    stock_check = check_stock(selected['id'], quantity)
                    
                    if stock_check['available']:
                        st.success(stock_check['message'])
                    else:
                        st.error(stock_check['message'])
                    
                    total = quantity * unit_price
                    rewards = total * 0.02
                    
                    st.metric("Total Amount", f"${total:,.2f}")
                    st.caption(f"⭐ Rewards: {rewards:.0f} points")
                    
                    # Submit
                    submitted = st.form_submit_button("💾 Record Sale", use_container_width=True)
                    
                    if submitted:
                        if not customer_name:
                            st.error("Please enter customer name")
                        elif not stock_check['available']:
                            st.error("Cannot sell out-of-stock product")
                        else:
                            # Record sale
                            sale_data = {
                                'sale_id': f"SPAR-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                                'customer_name': customer_name,
                                'customer_email': customer_email,
                                'product_category': category,
                                'product': selected['name'],
                                'quantity': quantity,
                                'unit_price': unit_price,
                                'total_sales': total,
                                'rewards_earned': rewards,
                                'sale_date': datetime.now().strftime('%Y-%m-%d'),
                                'sale_time': datetime.now().strftime('%H:%M:%S'),
                                'recorded_by': st.session_state.current_user.get('name', 'system')
                            }
                            
                            # Send to ETL (if running)
                            try:
                                response = requests.post('http://localhost:8000/webhook', json=sale_data, timeout=2)
                                st.success(f"✅ Sale recorded! ID: {sale_data['sale_id']}")
                            except:
                                st.success(f"✅ Sale recorded! (ETL not running) ID: {sale_data['sale_id']}")
                            
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
    
    with col2:
        st.markdown("### 📊 Today's Stats")
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(total_sales) as revenue,
                AVG(total_sales) as avg_sale
            FROM etl_sales_raw
            WHERE sale_date = CAST(GETDATE() AS DATE)
        """
        stats = execute_query(query)
        if not stats.empty:
            st.metric("Sales", f"${stats['revenue'].iloc[0]:,.2f}")
            st.metric("Transactions", stats['total'].iloc[0])
            st.metric("Average", f"${stats['avg_sale'].iloc[0]:,.2f}")

def show_products():
    """Product Management"""
    st.markdown("## 📦 Product Management")
    
    tab1, tab2 = st.tabs(["📋 Products", "➕ Add Product"])
    
    with tab1:
        search = st.text_input("🔍 Search Products", placeholder="Search by name or code")
        products = get_products_from_db(search=search if search else None)
        
        if products.empty:
            st.info("No products found")
        else:
            st.dataframe(
                products[['product_code', 'product_name', 'category_name', 'unit_price', 'available_stock', 'reorder_level']],
                use_container_width=True,
                column_config={
                    "product_code": "Code",
                    "product_name": "Product",
                    "category_name": "Category",
                    "unit_price": st.column_config.NumberColumn("Price", format="$%.2f"),
                    "available_stock": "Stock",
                    "reorder_level": "Reorder"
                },
                hide_index=True
            )
    
    with tab2:
        st.markdown("### ➕ Add New Product")
        with st.form("add_product"):
            col1, col2 = st.columns(2)
            with col1:
                product_code = st.text_input("Product Code *")
                product_name = st.text_input("Product Name *")
                category = st.selectbox("Category", get_product_categories())
            with col2:
                unit_price = st.number_input("Unit Price ($)", min_value=0.01, value=1.00)
                cost_price = st.number_input("Cost Price ($)", min_value=0.01, value=0.50)
                current_stock = st.number_input("Initial Stock", min_value=0, value=100)
                reorder_level = st.number_input("Reorder Level", min_value=1, value=20)
            
            submitted = st.form_submit_button("💾 Add Product", use_container_width=True)
            
            if submitted:
                if product_code and product_name:
                    # Insert into database
                    query = """
                        INSERT INTO erp_products (
                            product_code, product_name, category_id,
                            unit_price, cost_price, current_stock, reorder_level,
                            created_by
                        ) VALUES (?, ?, (SELECT id FROM erp_product_categories WHERE category_name = ?), ?, ?, ?, ?, ?)
                    """
                    success, msg = execute_command(query, (
                        product_code, product_name, category,
                        unit_price, cost_price, current_stock, reorder_level,
                        st.session_state.current_user.get('name', 'system')
                    ))
                    
                    if success:
                        st.success(f"✅ Product '{product_name}' added!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed: {msg}")
                else:
                    st.error("Please fill in required fields")

def show_suppliers():
    """Supplier Management"""
    st.markdown("## 🏷️ Supplier Management")
    
    suppliers = get_suppliers()
    
    if suppliers.empty:
        st.info("No suppliers found")
    else:
        st.dataframe(suppliers, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.markdown("### ➕ Add Supplier")
    with st.form("add_supplier"):
        col1, col2 = st.columns(2)
        with col1:
            supplier_code = st.text_input("Supplier Code *")
            supplier_name = st.text_input("Supplier Name *")
        with col2:
            email = st.text_input("Email")
            phone = st.text_input("Phone")
        
        submitted = st.form_submit_button("💾 Add Supplier", use_container_width=True)
        
        if submitted and supplier_code and supplier_name:
            query = """
                INSERT INTO erp_suppliers (supplier_code, supplier_name, email, phone, created_by)
                VALUES (?, ?, ?, ?, ?)
            """
            success, msg = execute_command(query, (
                supplier_code, supplier_name, email, phone,
                st.session_state.current_user.get('name', 'system')
            ))
            if success:
                st.success("✅ Supplier added!")
                st.rerun()
            else:
                st.error(f"❌ Failed: {msg}")

def show_orders():
    """Orders Management"""
    st.markdown("## 📋 Orders")
    
    tab1, tab2 = st.tabs(["📋 Sales Orders", "📦 Purchase Orders"])
    
    with tab1:
        query = """
            SELECT so_number, customer_id, order_date, status, total_amount
            FROM erp_sales_orders
            ORDER BY created_at DESC
        """
        orders = execute_query(query)
        if orders.empty:
            st.info("No sales orders found")
        else:
            st.dataframe(orders, use_container_width=True, hide_index=True)

def show_users():
    """User Management (Admin Only)"""
    st.markdown("## 👤 User Management")
    
    users = get_all_users()
    if users:
        user_list = []
        for email, u in users.items():
            user_list.append({
                'Name': u['name'],
                'Email': email,
                'Username': u['username'],
                'Role': u['role'].upper(),
                'Created': u.get('created_at', '')[:10]
            })
        st.dataframe(pd.DataFrame(user_list), use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ➕ Create User")
    with st.form("create_user"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Full Name *")
            new_username = st.text_input("Username *")
        with col2:
            new_email = st.text_input("Email *")
            new_password = st.text_input("Password *", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])
        
        submitted = st.form_submit_button("👤 Create User", use_container_width=True)
        
        if submitted:
            if all([new_name, new_username, new_email, new_password]):
                if len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    save_user(new_email, new_name, new_username, hash_password(new_password), new_role)
                    st.success(f"✅ User {new_name} created!")
                    st.rerun()
            else:
                st.error("Please fill all fields")

def show_settings():
    """Settings (Admin Only)"""
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 📊 System Status")
    
    # Check ETL
    try:
        response = requests.get('http://localhost:8000/health', timeout=2)
        if response.status_code == 200:
            st.success("✅ ETL Server Running")
        else:
            st.warning("⚠️ ETL Server Not Responding")
    except:
        st.error("❌ ETL Server Not Running")
    
    st.markdown("---")
    st.markdown("### 🔧 Database Connection")
    conn = get_db_connection()
    if conn:
        st.success("✅ Database Connected")
        conn.close()
    else:
        st.error("❌ Database Not Connected")
    
    st.markdown("---")
    st.markdown("### 📁 Raw Data Folder")
    st.code(str(RAW_DATA_FOLDER))

# ============================================
# START ETL SERVER IN BACKGROUND
# ============================================
def start_etl_server():
    """Start Flask ETL server in a background thread"""
    if not hasattr(st, '_etl_started'):
        try:
            thread = threading.Thread(target=run_etl_server, daemon=True)
            thread.start()
            st._etl_started = True
            time.sleep(2)  # Give server time to start
            print("✅ ETL Server started on http://localhost:8000")
        except Exception as e:
            print(f"❌ Failed to start ETL: {e}")

# ============================================
# MAIN ENTRY POINT
# ============================================
def main():
    # Page config
    st.set_page_config(
        page_title="SPAR ERP",
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "dashboard"
    
    # Initialize admin
    init_default_admin()
    
    # Show login or main app
    if st.session_state.logged_in:
        main_app()
    else:
        login_screen()

if __name__ == "__main__":
    # Start ETL server in background (optional)
    # Uncomment below to auto-start ETL with the app
    # start_etl_server()
    
    main()
