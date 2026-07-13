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
import base64

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
    page_title="SPAR Dynamics 365",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CUSTOM CSS - SPAR STYLING
# ============================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * { margin: 0; padding: 0; box-sizing: border-box; }
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background: #f0f2f5 !important;
        color: #202124 !important;
    }
    
    .stApp {
        background: #f0f2f5 !important;
    }
    
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        margin: 0 !important;
    }
    
    .st-emotion-cache-1v0mbdj {
        padding: 0 !important;
    }
    
    .st-emotion-cache-1avcm0n {
        padding: 0 !important;
    }
    
    .st-emotion-cache-6qob1r {
        padding: 0 !important;
    }
    
    /* SPAR Logo Styles */
    .spar-logo { display: flex; align-items: center; gap: 0.5rem; }
    .spar-logo .logo-icon { 
        background: #E3000F; 
        color: white; 
        font-weight: 800; 
        font-size: 1.3rem; 
        padding: 0.2rem 0.7rem; 
        border-radius: 4px; 
        letter-spacing: 1.5px; 
    }
    .spar-logo .logo-text { 
        font-weight: 700; 
        color: white; 
        font-size: 1.1rem; 
        letter-spacing: 0.5px; 
    }
    .spar-logo .logo-year { 
        font-weight: 300; 
        font-size: 0.7rem; 
        opacity: 0.7; 
        color: white; 
        background: rgba(255,255,255,0.15); 
        padding: 0.1rem 0.6rem; 
        border-radius: 12px; 
    }
    
    .spar-logo-big { margin-bottom: 1rem; }
    .spar-logo-big .logo-icon { 
        background: #E3000F; 
        color: white; 
        font-weight: 800; 
        font-size: 2.5rem; 
        padding: 0.3rem 1.2rem; 
        border-radius: 8px; 
        letter-spacing: 2px; 
        display: inline-block; 
    }
    .spar-logo-big .logo-year { 
        font-size: 0.8rem; 
        color: #6B7280; 
        display: block; 
        margin-top: 0.3rem; 
    }
    
    /* Login Screen */
    .login-container { 
        display: flex; 
        justify-content: center; 
        align-items: center; 
        min-height: 100vh; 
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f4e 50%, #2d1b69 100%);
    }
    
    .login-box { 
        background: rgba(255, 255, 255, 0.95); 
        backdrop-filter: blur(20px); 
        border-radius: 20px; 
        padding: 3rem; 
        max-width: 420px; 
        width: 100%; 
        box-shadow: 0 20px 60px rgba(0,0,0,0.5); 
        text-align: center; 
        border: 1px solid rgba(255,255,255,0.2); 
    }
    
    .login-box .subtitle { 
        font-size: 0.85rem; 
        color: #6B7280; 
        margin-bottom: 2rem; 
    }
    
    .login-box .form-group { 
        margin-bottom: 1rem; 
        text-align: left; 
    }
    
    .login-box .form-group label { 
        display: block; 
        font-size: 0.8rem; 
        font-weight: 500; 
        color: #202124; 
        margin-bottom: 0.3rem; 
    }
    
    .login-box .form-group input { 
        width: 100%; 
        padding: 0.6rem 0.75rem; 
        border: 1px solid #dadce0; 
        border-radius: 8px; 
        font-size: 0.9rem; 
        background: white;
        color: #202124;
    }
    
    .login-box .form-group input:focus { 
        outline: none; 
        border-color: #0052A5; 
        box-shadow: 0 0 0 2px rgba(0,82,165,0.1); 
    }
    
    .login-box .btn-login { 
        width: 100%; 
        padding: 0.6rem; 
        background: #002B5C; 
        color: white; 
        border: none; 
        border-radius: 8px; 
        font-size: 1rem; 
        font-weight: 600; 
        cursor: pointer; 
        transition: all 0.2s; 
    }
    
    .login-box .btn-login:hover { 
        background: #004080; 
        transform: translateY(-1px); 
        box-shadow: 0 4px 12px rgba(0,43,92,0.3); 
    }
    
    .login-box .footer { 
        margin-top: 1.5rem; 
        font-size: 0.7rem; 
        color: #9AA0A6; 
    }
    
    /* Top Navigation */
    .top-nav { 
        background: linear-gradient(135deg, #002B5C 0%, #004080 50%, #0052A5 100%); 
        padding: 0.5rem 2rem; 
        display: flex; 
        align-items: center; 
        justify-content: space-between; 
        height: 60px; 
        box-shadow: 0 2px 8px rgba(0,0,0,0.15); 
        position: sticky; 
        top: 0; 
        left: 0; 
        right: 0; 
        z-index: 1000; 
    }
    
    .top-nav .brand { 
        display: flex; 
        align-items: center; 
        gap: 0.75rem; 
    }
    
    .top-nav .brand .version { 
        font-weight: 400; 
        font-size: 0.65rem; 
        opacity: 0.7; 
        background: rgba(255,255,255,0.15); 
        padding: 0.1rem 0.6rem; 
        border-radius: 12px; 
        margin-left: 0.5rem; 
    }
    
    .top-nav .nav-actions { 
        display: flex; 
        align-items: center; 
        gap: 1.5rem; 
    }
    
    .top-nav .nav-actions .search-box { 
        background: rgba(255,255,255,0.15); 
        border-radius: 20px; 
        padding: 0.35rem 1rem; 
        display: flex; 
        align-items: center; 
        gap: 0.5rem; 
        border: 1px solid rgba(255,255,255,0.1); 
        min-width: 200px; 
    }
    
    .top-nav .nav-actions .search-box input { 
        background: transparent; 
        border: none; 
        color: white; 
        outline: none; 
        width: 100%; 
        font-size: 0.85rem; 
    }
    
    .top-nav .nav-actions .search-box input::placeholder { 
        color: rgba(255,255,255,0.6); 
    }
    
    .top-nav .nav-actions .icon-btn { 
        color: rgba(255,255,255,0.8); 
        background: none; 
        border: none; 
        font-size: 1.1rem; 
        cursor: pointer; 
        padding: 0.4rem; 
        border-radius: 50%; 
        transition: all 0.2s; 
        width: 36px; 
        height: 36px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        position: relative; 
    }
    
    .top-nav .nav-actions .icon-btn:hover { 
        background: rgba(255,255,255,0.15); 
        color: white; 
    }
    
    .top-nav .nav-actions .icon-btn .badge { 
        position: absolute; 
        top: 2px; 
        right: 2px; 
        background: #dc3545; 
        color: white; 
        font-size: 0.55rem; 
        border-radius: 50%; 
        padding: 0.1rem 0.4rem; 
        font-weight: 600; 
        min-width: 18px; 
        text-align: center; 
    }
    
    .top-nav .user-profile { 
        display: flex; 
        align-items: center; 
        gap: 0.75rem; 
        color: white; 
        cursor: pointer; 
        padding: 0.2rem 0.8rem 0.2rem 0.5rem; 
        border-radius: 24px; 
        transition: all 0.2s; 
    }
    
    .top-nav .user-profile:hover { 
        background: rgba(255,255,255,0.1); 
    }
    
    .top-nav .user-profile .avatar { 
        width: 32px; 
        height: 32px; 
        border-radius: 50%; 
        background: rgba(255,255,255,0.2); 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        font-weight: 600; 
        font-size: 0.8rem; 
    }
    
    .top-nav .user-profile .name { 
        font-size: 0.85rem; 
        font-weight: 500; 
    }
    
    .top-nav .user-profile .role { 
        font-size: 0.65rem; 
        opacity: 0.7; 
        font-weight: 400; 
    }
    
    /* Sidebar */
    .sidebar { 
        position: sticky; 
        top: 60px; 
        float: left;
        width: 220px; 
        height: calc(100vh - 60px);
        background: #1a2a3a; 
        color: white; 
        overflow-y: auto; 
        z-index: 999; 
        transition: width 0.3s; 
        padding-bottom: 2rem;
    }
    
    .sidebar::-webkit-scrollbar { width: 4px; }
    .sidebar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }
    
    .sidebar .menu-section { padding: 0.5rem 0; }
    .sidebar .menu-section .section-title { 
        font-size: 0.6rem; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
        color: rgba(255,255,255,0.3); 
        padding: 0.75rem 1.2rem 0.5rem 1.2rem; 
        font-weight: 600; 
    }
    
    .sidebar .menu-item { 
        display: flex; 
        align-items: center; 
        gap: 0.75rem; 
        padding: 0.6rem 1.2rem; 
        color: rgba(255,255,255,0.7); 
        text-decoration: none; 
        cursor: pointer; 
        transition: all 0.2s; 
        border-left: 3px solid transparent; 
        font-size: 0.85rem; 
        font-weight: 500; 
        background: transparent;
        border: none;
        width: 100%;
        text-align: left;
    }
    
    .sidebar .menu-item:hover { 
        background: rgba(255,255,255,0.08); 
        color: white; 
    }
    
    .sidebar .menu-item.active { 
        background: rgba(255,255,255,0.12); 
        color: white; 
        border-left-color: #5e9bff; 
    }
    
    .sidebar .menu-item i { width: 20px; text-align: center; font-size: 1rem; }
    .sidebar .menu-item .badge { 
        margin-left: auto; 
        background: #dc3545; 
        color: white; 
        font-size: 0.6rem; 
        padding: 0.1rem 0.5rem; 
        border-radius: 12px; 
        font-weight: 600; 
    }
    
    .sidebar .menu-item .badge.warning { background: #ffc107; color: #212529; }
    
    /* Main Content */
    .main-content { 
        margin-left: 220px; 
        padding: 1.5rem 2rem; 
        background: #f0f2f5; 
        min-height: calc(100vh - 60px);
    }
    
    /* Page Header */
    .page-header { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        margin-bottom: 1.5rem; 
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .page-header h1 { 
        font-size: 1.5rem; 
        font-weight: 600; 
        color: #002B5C; 
    }
    
    .page-header .subtitle { 
        color: #6B7280; 
        font-size: 0.85rem; 
        margin-top: 0.2rem; 
    }
    
    .page-header .actions { 
        display: flex; 
        gap: 0.5rem; 
        flex-wrap: wrap; 
    }
    
    .page-header .actions .btn { 
        padding: 0.5rem 1.2rem; 
        border-radius: 8px; 
        border: none; 
        font-weight: 500; 
        font-size: 0.8rem; 
        cursor: pointer; 
        transition: all 0.2s; 
        display: flex; 
        align-items: center; 
        gap: 0.5rem; 
    }
    
    .page-header .actions .btn-primary { background: #002B5C; color: white; }
    .page-header .actions .btn-primary:hover { background: #004080; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,43,92,0.3); }
    .page-header .actions .btn-success { background: #28a745; color: white; }
    .page-header .actions .btn-success:hover { background: #218838; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(40,167,69,0.3); }
    .page-header .actions .btn-outline { background: transparent; color: #002B5C; border: 1px solid #e8eaed; }
    .page-header .actions .btn-outline:hover { background: #f0f2f5; }
    
    /* Metrics Grid */
    .metrics-grid { 
        display: grid; 
        grid-template-columns: repeat(4, 1fr); 
        gap: 1rem; 
        margin-bottom: 1.5rem; 
    }
    
    .metric-card { 
        background: white; 
        border-radius: 12px; 
        padding: 1.25rem; 
        border: 1px solid #e8eaed; 
        transition: all 0.2s; 
        position: relative; 
        overflow: hidden; 
    }
    
    .metric-card:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 4px 16px rgba(0,0,0,0.06); 
    }
    
    .metric-card .icon { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .metric-card .value { 
        font-size: 1.8rem; 
        font-weight: 700; 
        color: #002B5C; 
        margin-bottom: 0.2rem; 
    }
    .metric-card .label { 
        font-size: 0.7rem; 
        color: #6B7280; 
        font-weight: 500; 
        text-transform: uppercase; 
        letter-spacing: 0.5px; 
    }
    .metric-card .trend { 
        font-size: 0.7rem; 
        margin-top: 0.3rem; 
        font-weight: 500; 
    }
    .metric-card .trend.up { color: #28a745; }
    .metric-card .trend.down { color: #dc3545; }
    .metric-card .indicator { 
        position: absolute; 
        top: 0; 
        right: 0; 
        width: 4px; 
        height: 100%; 
    }
    .metric-card .indicator.blue { background: #0052A5; }
    .metric-card .indicator.green { background: #28a745; }
    .metric-card .indicator.yellow { background: #ffc107; }
    .metric-card .indicator.red { background: #dc3545; }
    .metric-card .indicator.purple { background: #6f42c1; }
    
    /* Quick Actions */
    .quick-actions { 
        display: grid; 
        grid-template-columns: repeat(6, 1fr); 
        gap: 0.75rem; 
        margin-bottom: 1.5rem; 
    }
    
    .quick-action { 
        background: white; 
        border: 1px solid #e8eaed; 
        border-radius: 10px; 
        padding: 1rem 0.5rem; 
        text-align: center; 
        cursor: pointer; 
        transition: all 0.2s; 
        text-decoration: none; 
        color: #202124; 
    }
    
    .quick-action:hover { 
        background: #002B5C; 
        color: white; 
        transform: translateY(-2px); 
        box-shadow: 0 4px 12px rgba(0,43,92,0.2); 
    }
    
    .quick-action i { 
        font-size: 1.5rem; 
        display: block; 
        margin-bottom: 0.3rem; 
    }
    
    .quick-action .label { font-size: 0.7rem; font-weight: 500; }
    .quick-action:hover .label { color: white; }
    
    /* Cards */
    .content-grid { 
        display: grid; 
        grid-template-columns: 2fr 1fr; 
        gap: 1.5rem; 
        margin-bottom: 1.5rem; 
    }
    
    .card { 
        background: white; 
        border-radius: 12px; 
        border: 1px solid #e8eaed; 
        overflow: hidden; 
    }
    
    .card .card-header { 
        padding: 1rem 1.25rem; 
        border-bottom: 1px solid #e8eaed; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        flex-wrap: wrap; 
    }
    
    .card .card-header h3 { 
        font-size: 0.9rem; 
        font-weight: 600; 
        color: #202124; 
    }
    
    .card .card-header .link { 
        font-size: 0.75rem; 
        color: #0052A5; 
        text-decoration: none; 
        font-weight: 500; 
        cursor: pointer; 
    }
    
    .card .card-header .link:hover { text-decoration: underline; }
    .card .card-body { padding: 1rem 1.25rem; overflow-x: auto; }
    
    /* Status Badges */
    .status-badge { 
        padding: 0.15rem 0.6rem; 
        border-radius: 12px; 
        font-size: 0.65rem; 
        font-weight: 600; 
        display: inline-block; 
    }
    .status-badge.draft { background: #e9ecef; color: #495057; }
    .status-badge.confirmed { background: #cce5ff; color: #004085; }
    .status-badge.shipped { background: #d1ecf1; color: #0c5460; }
    .status-badge.delivered { background: #d4edda; color: #155724; }
    .status-badge.cancelled { background: #f8d7da; color: #721c24; }
    .status-badge.open { background: #fff3cd; color: #856404; }
    .status-badge.paid { background: #d4edda; color: #155724; }
    .status-badge.overdue { background: #f8d7da; color: #721c24; }
    .status-badge.received { background: #d4edda; color: #155724; }
    .status-badge.partial { background: #fff3cd; color: #856404; }
    .status-badge.synced { background: #d4edda; color: #155724; }
    .status-badge.processing { background: #cce5ff; color: #004085; }
    .status-badge.in-stock { background: #d4edda; color: #155724; }
    .status-badge.low-stock { background: #fff3cd; color: #856404; }
    .status-badge.out-of-stock { background: #f8d7da; color: #721c24; }
    
    /* Toast Notification */
    .toast { 
        position: fixed; 
        bottom: 2rem; 
        right: 2rem; 
        padding: 1rem 1.5rem; 
        border-radius: 12px; 
        color: white; 
        font-weight: 500; 
        z-index: 3000; 
        animation: slideIn 0.3s ease; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.15); 
    }
    .toast.success { background: #28a745; }
    .toast.error { background: #dc3545; }
    .toast.info { background: #0052A5; }
    
    @keyframes slideIn { 
        from { transform: translateY(20px); opacity: 0; } 
        to { transform: translateY(0); opacity: 1; } 
    }
    
    /* Activity List */
    .activity-list { list-style: none; }
    .activity-list li { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 0.6rem 0; 
        border-bottom: 1px solid #f0f2f5; 
    }
    .activity-list li:last-child { border-bottom: none; }
    .activity-list .info .title { font-weight: 500; font-size: 0.85rem; }
    .activity-list .info .meta { font-size: 0.7rem; color: #6B7280; }
    .activity-list .amount { font-weight: 600; font-size: 0.85rem; }
    
    /* Product Grid */
    .product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
    .product-card { 
        background: white; 
        border-radius: 12px; 
        padding: 1rem; 
        border: 1px solid #e8eaed; 
        transition: all 0.2s; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
    }
    .product-card:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 4px 12px rgba(0,0,0,0.06); 
    }
    .product-card .info .name { 
        font-weight: 600; 
        font-size: 0.9rem; 
        color: #002B5C; 
    }
    .product-card .info .code { font-size: 0.7rem; color: #6B7280; }
    .product-card .info .category { 
        font-size: 0.7rem; 
        color: #6B7280; 
        background: #f0f2f5; 
        padding: 0.1rem 0.6rem; 
        border-radius: 12px; 
    }
    .product-card .stock { text-align: right; }
    .product-card .stock .qty { font-weight: 700; font-size: 1.1rem; }
    .product-card .stock .qty.in-stock { color: #28a745; }
    .product-card .stock .qty.low-stock { color: #f39c12; }
    .product-card .stock .qty.out-of-stock { color: #dc3545; }
    
    /* Filter Bar */
    .filter-bar { 
        display: flex; 
        gap: 1rem; 
        flex-wrap: wrap; 
        margin-bottom: 1rem; 
    }
    .filter-bar input, .filter-bar select { 
        padding: 0.4rem 0.75rem; 
        border: 1px solid #dadce0; 
        border-radius: 8px; 
        font-size: 0.85rem; 
        font-family: 'Inter', sans-serif; 
        background: white; 
        color: #202124;
    }
    
    /* Responsive */
    @media (max-width: 1200px) { 
        .metrics-grid { grid-template-columns: repeat(2, 1fr); } 
        .quick-actions { grid-template-columns: repeat(3, 1fr); } 
        .content-grid { grid-template-columns: 1fr; } 
    }
    
    @media (max-width: 768px) { 
        .sidebar { display: none; } 
        .main-content { margin-left: 0; } 
        .top-nav .nav-actions .search-box { min-width: 120px; } 
        .metrics-grid { grid-template-columns: 1fr; } 
        .quick-actions { grid-template-columns: repeat(2, 1fr); } 
        .top-nav .user-profile .name, .top-nav .user-profile .role { display: none; } 
        .login-box { padding: 2rem; } 
        .page-header { flex-direction: column; align-items: flex-start; gap: 0.5rem; } 
    }
    
    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    .st-emotion-cache-1r6slb0 {padding: 0 !important;}
</style>
""", unsafe_allow_html=True)

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
    <div class="login-container">
        <div class="login-box">
            <div class="spar-logo-big">
                <span class="logo-icon">SPAR</span>
                <span class="logo-year">2026</span>
            </div>
            <div class="subtitle">Enterprise Resource Planning</div>
            <div style="background: #f1f5f9; padding: 0.75rem; border-radius: 8px; text-align: left; margin-top: 0.75rem; font-size: 0.7rem;">
                <strong>How to configure:</strong><br><br>
                1. Go to Settings → Secrets<br>
                2. Add: <code>WEBHOOK_URL = "https://your-tunnel-url.trycloudflare.com/webhook"</code><br>
                3. Replace with your actual tunnel URL<br>
                4. Click Save and Restart
            </div>
            <div class="footer">© 2026 SPAR International | Yellowcob Enterprises Pvt Ltd</div>
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
        save_user("admin@spar.com", "System Administrator", "admin", hash_password("Admin@123"), "admin")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def register_user(name, username, email, password, role="operator"):
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
    return True, f"User {name} created successfully!"

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
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

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
# SPAR UI COMPONENTS
# ============================================
def render_spar_nav():
    user = st.session_state.current_user
    if not user:
        return
    
    is_admin = user['role'] == 'admin'
    
    st.markdown(f"""
    <nav class="top-nav">
        <div class="brand">
            <div class="spar-logo">
                <span class="logo-icon">SPAR</span>
                <span class="logo-text">Dynamics 365</span>
                <span class="logo-year">2026</span>
            </div>
        </div>
        
        <div class="nav-actions">
            <div class="search-box">
                <i class="fas fa-search"></i>
                <input type="text" placeholder="Search (Ctrl+E)" id="globalSearch">
                <span style="font-size: 0.6rem; opacity: 0.5; font-weight: 400;">⌘E</span>
            </div>
            
            <button class="icon-btn" onclick="alert('No new notifications')">
                <i class="fas fa-bell"></i>
                <span class="badge">0</span>
            </button>
            
            <button class="icon-btn" onclick="alert('SPAR Dynamics 365 v2.0\\n© 2026 Yellowcob Enterprises Pvt Ltd')">
                <i class="fas fa-question-circle"></i>
            </button>
            
            <div class="user-profile">
                <div class="avatar">{user['name'][0].upper()}</div>
                <div>
                    <div class="name">{user['name']}</div>
                    <div class="role">{'Administrator' if is_admin else 'Operator'}</div>
                </div>
                <i class="fas fa-chevron-down" style="font-size: 0.6rem; opacity: 0.5;"></i>
            </div>
        </div>
    </nav>
    """, unsafe_allow_html=True)

def render_spar_sidebar():
    user = st.session_state.current_user
    if not user:
        return
    
    is_admin = user['role'] == 'admin'
    current_page = st.session_state.current_page
    
    menu_items = [
        {"id": "dashboard", "icon": "fa-chart-pie", "label": "Dashboard"},
        {"id": "sales", "icon": "fa-plus-circle", "label": "New Sale", "badge": "warning"},
        {"id": "sales_orders", "icon": "fa-file-invoice", "label": "Sales Orders", "badge": "0"},
        {"id": "my_sales", "icon": "fa-user-tie", "label": "My Sales"},
    ]
    
    admin_items = [
        {"id": "users", "icon": "fa-user-cog", "label": "User Management"},
        {"id": "settings", "icon": "fa-sliders-h", "label": "System Settings"},
    ]
    
    st.markdown('<nav class="sidebar" id="sidebarMenu">', unsafe_allow_html=True)
    st.markdown('<div class="menu-section"><div class="section-title">SALES</div>', unsafe_allow_html=True)
    
    for item in menu_items:
        active = "active" if current_page == item['id'] else ""
        badge_html = f'<span class="badge {item.get("badge", "")}">{item.get("badge", "")}</span>' if item.get('badge') else ""
        st.markdown(f"""
        <button class="menu-item {active}" onclick="window.location.href='?page={item['id']}'">
            <i class="fas {item['icon']}"></i>
            <span>{item['label']}</span>
            {badge_html}
        </button>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if is_admin:
        st.markdown('<div class="menu-section"><div class="section-title">ADMINISTRATION</div>', unsafe_allow_html=True)
        for item in admin_items:
            active = "active" if current_page == item['id'] else ""
            st.markdown(f"""
            <button class="menu-item {active}" onclick="window.location.href='?page={item['id']}'">
                <i class="fas {item['icon']}"></i>
                <span>{item['label']}</span>
            </button>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="menu-section">
        <button class="menu-item" onclick="window.location.href='?logout=true'" style="border-left-color: #dc3545;">
            <i class="fas fa-sign-out-alt"></i>
            <span>Sign Out</span>
        </button>
    </div>
    </nav>
    """, unsafe_allow_html=True)

# ============================================
# PAGE FUNCTIONS
# ============================================
def render_dashboard():
    user = st.session_state.current_user
    is_admin = user['role'] == 'admin'
    user_name = user['name']
    
    st.markdown(f"""
    <div class="main-content">
        <div class="page-header">
            <div>
                <h1>📊 Role Center</h1>
                <div class="subtitle">Good afternoon! Here's your business overview. 
                    {'👑 Admin - Viewing ALL sales' if is_admin else '👤 Operator - Viewing your sales only'} (Last 24 hours)
                </div>
            </div>
            <div class="actions">
                <button class="btn btn-success" onclick="window.location.href='?page=sales'">
                    <i class="fas fa-plus"></i> New Sale
                </button>
                <button class="btn btn-primary" onclick="window.location.href='?page=sales'">
                    <i class="fas fa-box"></i> Add Product
                </button>
                <button class="btn btn-outline" onclick="window.location.reload()">
                    <i class="fas fa-sync"></i> Refresh
                </button>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown("""
    <div class="quick-actions">
        <div class="quick-action" onclick="window.location.href='?page=sales'">
            <i class="fas fa-shopping-cart"></i>
            <span class="label">New Sale</span>
        </div>
        <div class="quick-action" onclick="window.location.href='?page=purchase'">
            <i class="fas fa-truck"></i>
            <span class="label">New PO</span>
        </div>
        <div class="quick-action" onclick="alert('Goods Receiving')">
            <i class="fas fa-warehouse"></i>
            <span class="label">Receive Goods</span>
        </div>
        <div class="quick-action" onclick="window.location.href='?page=products'">
            <i class="fas fa-boxes"></i>
            <span class="label">Products</span>
        </div>
        <div class="quick-action" onclick="window.location.href='?page=sales'">
            <i class="fas fa-plus-circle"></i>
            <span class="label">Add Product</span>
        </div>
        <div class="quick-action" onclick="window.location.href='?page=my_sales'">
            <i class="fas fa-user-tie"></i>
            <span class="label">My Sales</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    try:
        sales_data = get_sales_from_db(operator_name=None if is_admin else user_name, date_filter='today')
        if sales_data:
            df = pd.DataFrame(sales_data)
            total_revenue = df['total_sales'].sum() if 'total_sales' in df.columns else 0
            transaction_count = len(df)
        else:
            total_revenue = 0
            transaction_count = 0
    except:
        total_revenue = 0
        transaction_count = 0
    
    st.markdown(f"""
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="indicator blue"></div>
            <div class="icon">💰</div>
            <div class="value">${total_revenue:,.2f}</div>
            <div class="label">{'Admin - All Sales' if is_admin else 'My Sales'} (Last 24h)</div>
            <div class="trend up">{transaction_count} transactions</div>
        </div>
        <div class="metric-card">
            <div class="indicator green"></div>
            <div class="icon">📦</div>
            <div class="value">150</div>
            <div class="label">Total Products</div>
            <div class="trend up">Active catalog</div>
        </div>
        <div class="metric-card">
            <div class="indicator yellow"></div>
            <div class="icon">⚠️</div>
            <div class="value">12</div>
            <div class="label">Low Stock Items</div>
            <div class="trend down">Need reorder</div>
        </div>
        <div class="metric-card">
            <div class="indicator red"></div>
            <div class="icon">📋</div>
            <div class="value">3</div>
            <div class="label">Pending POs</div>
            <div class="trend down">Awaiting delivery</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Content Grid
    st.markdown("""
    <div class="content-grid">
        <div class="card">
            <div class="card-header">
                <h3>📈 Sales Trend (Last 7 Days)</h3>
                <span class="link">View all →</span>
            </div>
            <div class="card-body">
                <div style="height:200px;display:flex;align-items:flex-end;padding:0 1rem;gap:0.5rem;">
    """, unsafe_allow_html=True)
    
    # Chart bars
    try:
        if sales_data:
            df = pd.DataFrame(sales_data)
            if 'sale_date' in df.columns:
                df['sale_date'] = pd.to_datetime(df['sale_date']).dt.date
                daily_sales = df.groupby('sale_date')['total_sales'].sum().reset_index()
                max_val = daily_sales['total_sales'].max() if not daily_sales.empty else 1
                for _, row in daily_sales.iterrows():
                    height = max(20, (row['total_sales'] / max_val) * 100) if max_val > 0 else 20
                    st.markdown(f'<div style="flex:1;height:{height}%;background:#0052A5;border-radius:6px 6px 0 0;min-height:20px;"></div>', unsafe_allow_html=True)
            else:
                for _ in range(7):
                    st.markdown('<div style="flex:1;height:40%;background:#0052A5;border-radius:6px 6px 0 0;min-height:20px;opacity:0.3;"></div>', unsafe_allow_html=True)
        else:
            for _ in range(7):
                st.markdown('<div style="flex:1;height:40%;background:#0052A5;border-radius:6px 6px 0 0;min-height:20px;opacity:0.3;"></div>', unsafe_allow_html=True)
    except:
        for _ in range(7):
            st.markdown('<div style="flex:1;height:40%;background:#0052A5;border-radius:6px 6px 0 0;min-height:20px;opacity:0.3;"></div>', unsafe_allow_html=True)
    
    st.markdown("""
                </div>
            </div>
        </div>
        <div class="card">
            <div class="card-header">
                <h3>📋 Recent Orders (Last 24h)</h3>
                <span class="link">View all →</span>
            </div>
            <div class="card-body">
                <ul class="activity-list">
    """, unsafe_allow_html=True)
    
    # Recent orders
    try:
        if sales_data:
            recent = sales_data[:5]
            for sale in recent:
                customer = sale.get('customer_name', 'Unknown')
                sale_id = sale.get('sale_id', 'N/A')
                total = sale.get('total_sales', 0)
                st.markdown(f"""
                <li>
                    <div class="info">
                        <div class="title">{sale_id}</div>
                        <div class="meta">{customer}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-weight:600;">${total:,.2f}</div>
                        <span class="status-badge synced">Synced</span>
                    </div>
                </li>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<li style="text-align:center;color:#6B7280;padding:1rem 0;">No orders in the last 24 hours</li>', unsafe_allow_html=True)
    except:
        st.markdown('<li style="text-align:center;color:#6B7280;padding:1rem 0;">No orders available</li>', unsafe_allow_html=True)
    
    st.markdown("""
                </ul>
            </div>
        </div>
    </div>
    </div>
    """, unsafe_allow_html=True)

def render_sales_form():
    user = st.session_state.current_user
    
    st.markdown("""
    <div class="main-content">
        <div class="page-header">
            <div>
                <h1>🛒 New Sale</h1>
                <div class="subtitle">Record a new customer purchase</div>
            </div>
            <div class="actions">
                <button class="btn btn-outline" onclick="window.location.href='?page=dashboard'">
                    <i class="fas fa-arrow-left"></i> Back
                </button>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        with st.container():
            st.markdown("""
            <div class="modern-card">
                <div class="card-header">📋 New Purchase</div>
            """, unsafe_allow_html=True)
            
            # Customer Details
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
            st.markdown('<p style="color: #202124; font-weight: 600;">🛍️ Purchase Details</p>', unsafe_allow_html=True)
            
            # Product Selection
            product_category = st.selectbox("Product Category", list(SPAR_PRODUCTS.keys()))
            products = SPAR_PRODUCTS.get(product_category, [])
            product = st.selectbox("Product", products)
            
            col_e, col_f = st.columns(2)
            with col_e:
                quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
            with col_f:
                unit_price = st.number_input("Unit Price (USD)", min_value=0.01, value=10.00, step=0.01, format="%.2f")
            
            total_sales = quantity * unit_price
            st.metric("Total Amount", f"${total_sales:,.2f}")
            st.caption(f"📅 Purchase Date: {datetime.now().strftime('%m/%d/%Y')}")
            
            rewards_earned = total_sales * 0.02
            st.info(f"⭐ Rewards Points Earned: {rewards_earned:.0f} (2% of purchase)")
            
            submitted = st.button("💾 Record Sale", use_container_width=True)
            
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
                        'customer_email': customer_email if customer_email else None,
                        'customer_id': customer_id if customer_id else None,
                        'phone': phone if phone else None,
                        'product_category': product_category,
                        'product': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_sales': total_sales_calc,
                        'rewards_earned': rewards_earned_calc,
                        'sale_date': now.strftime('%Y-%m-%d'),
                        'sale_time': now.strftime('%H:%M:%S'),
                        'timestamp_utc': now.isoformat(),
                        'recorded_by': user['name']
                    }
                    
                    success, message = send_to_webhook(data)
                    send_admin_notification(customer_name, sale_id, product, quantity, total_sales_calc, rewards_earned_calc, customer_email)
                    
                    if success:
                        st.success(f"✅ Sale recorded! ID: {sale_id}")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning(f"⚠️ {message}")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col_right:
        st.markdown("""
        <div class="modern-card">
            <div class="card-header">📊 System Status</div>
        """, unsafe_allow_html=True)
        
        if check_connection():
            st.success("✅ ETL Connected")
            st.info("📤 Data is being sent to SQL Server")
        else:
            st.warning("⚠️ ETL Offline - Tunnel may be down")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_sales_orders():
    st.markdown("""
    <div class="main-content">
        <div class="page-header">
            <div>
                <h1>📋 Sales Orders</h1>
                <div class="subtitle">View all sales orders and invoices</div>
            </div>
            <div class="actions">
                <button class="btn btn-success" onclick="window.location.href='?page=sales'">
                    <i class="fas fa-plus"></i> New Sale
                </button>
                <button class="btn btn-outline" onclick="window.location.reload()">
                    <i class="fas fa-sync"></i> Refresh
                </button>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3>📋 Sales Orders</h3>
                <span class="link">Loading orders...</span>
            </div>
            <div class="card-body">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Order #</th>
                                <th>Customer</th>
                                <th>Date</th>
                                <th>Total</th>
                                <th>Status</th>
                                <th>Approval</th>
                                <th>Rewards</th>
                            </tr>
                        </thead>
                        <tbody>
    """, unsafe_allow_html=True)
    
    try:
        sales_data = get_sales_from_db()
        if sales_data:
            for sale in sales_data[:10]:
                st.markdown(f"""
                <tr>
                    <td><strong>{sale.get('sale_id', 'N/A')}</strong></td>
                    <td>{sale.get('customer_name', 'Unknown')}</td>
                    <td>{sale.get('sale_date', 'N/A')}</td>
                    <td><strong>${sale.get('total_sales', 0):,.2f}</strong></td>
                    <td><span class="status-badge confirmed">Confirmed</span></td>
                    <td><span class="status-badge synced">Approved</span></td>
                    <td>{sale.get('rewards_earned', 0):.0f} pts</td>
                </tr>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<tr><td colspan="7" style="text-align:center;padding:1rem 0;">No sales orders found</td></tr>', unsafe_allow_html=True)
    except:
        st.markdown('<tr><td colspan="7" style="text-align:center;padding:1rem 0;">Error loading orders</td></tr>', unsafe_allow_html=True)
    
    st.markdown("""
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_my_sales():
    user = st.session_state.current_user
    user_name = user['name']
    
    st.markdown(f"""
    <div class="main-content">
        <div class="page-header">
            <div>
                <h1>👤 My Sales</h1>
                <div class="subtitle">View your recorded sales</div>
            </div>
            <div class="actions">
                <button class="btn btn-success" onclick="window.location.href='?page=sales'">
                    <i class="fas fa-plus"></i> New Sale
                </button>
                <button class="btn btn-outline" onclick="window.location.reload()">
                    <i class="fas fa-sync"></i> Refresh
                </button>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    try:
        sales_data = get_sales_from_db(operator_name=user_name)
        if sales_data:
            df = pd.DataFrame(sales_data)
            total_revenue = df['total_sales'].sum() if 'total_sales' in df.columns else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
            with col2:
                st.metric("Transactions", len(df))
            with col3:
                avg_sale = df['total_sales'].mean() if 'total_sales' in df.columns else 0
                st.metric("Average Sale", f"${avg_sale:.2f}")
            with col4:
                customers = df['customer_name'].nunique() if 'customer_name' in df.columns else 0
                st.metric("Customers Served", customers)
            
            st.markdown("#### Sales Details")
            display_cols = ['sale_id', 'customer_name', 'product', 'quantity', 'total_sales', 'sale_time']
            available_cols = [c for c in display_cols if c in df.columns]
            if available_cols:
                st.dataframe(df[available_cols], use_container_width=True, height=300)
        else:
            st.info("No sales recorded")
    except:
        st.warning("Error loading sales data")
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_users():
    user = st.session_state.current_user
    if user['role'] != 'admin':
        st.error("❌ You do not have permission to view this page.")
        return
    
    st.markdown("""
    <div class="main-content">
        <div class="page-header">
            <div>
                <h1>👤 User Management</h1>
                <div class="subtitle">Manage system users</div>
            </div>
            <div class="actions">
                <button class="btn btn-primary" onclick="window.location.href='?page=users&action=add'">
                    <i class="fas fa-user-plus"></i> Add User
                </button>
                <button class="btn btn-outline" onclick="window.location.reload()">
                    <i class="fas fa-sync"></i> Refresh
                </button>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Handle add user action
    if st.session_state.get('page_action') == 'add':
        with st.container():
            st.markdown('<div class="modern-card"><div class="card-header">👤 Create New User</div>', unsafe_allow_html=True)
            
            with st.form("create_user_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Full Name *")
                    username = st.text_input("Username *")
                with col2:
                    email = st.text_input("Email *")
                    password = st.text_input("Password *", type="password")
                    role = st.selectbox("Role", ["operator", "admin"])
                
                submitted = st.form_submit_button("👤 Create User", use_container_width=True)
                
                if submitted:
                    if not all([name, username, email, password]):
                        st.error("Please fill all fields")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        success, message = register_user(name, username, email, password, role)
                        if success:
                            st.success(message)
                            st.session_state.page_action = None
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error(message)
            
            st.markdown('</div>', unsafe_allow_html=True)
            if st.button("Cancel"):
                st.session_state.page_action = None
                st.rerun()
    
    # List users
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
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_settings():
    user = st.session_state.current_user
    if user['role'] != 'admin':
        st.error("❌ You do not have permission to view this page.")
        return
    
    st.markdown("""
    <div class="main-content">
        <div class="page-header">
            <div>
                <h1>⚙️ System Settings</h1>
                <div class="subtitle">View system configuration</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="modern-card"><div class="card-header">📊 System Status</div>', unsafe_allow_html=True)
        if check_connection():
            st.success("✅ ETL Server Connected")
        else:
            st.error("❌ ETL Server Offline")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="modern-card"><div class="card-header">🔧 Configuration</div>', unsafe_allow_html=True)
        st.code(f"WEBHOOK_URL = {WEBHOOK_URL}", language="python")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# LOGIN SCREEN
# ============================================
def render_login():
    st.markdown("""
    <div class="login-container">
        <div class="login-box">
            <div class="spar-logo-big">
                <span class="logo-icon">SPAR</span>
                <span class="logo-year">2026</span>
            </div>
            <div class="subtitle">Enterprise Resource Planning</div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="collapsed")
        
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
    
    st.markdown("""
            <div class="footer">© 2026 SPAR International | Yellowcob Enterprises Pvt Ltd</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# MAIN APP
# ============================================
def main():
    # Handle logout
    if st.query_params.get('logout') == 'true':
        logout_user()
        st.query_params.clear()
        st.rerun()
    
    # Handle page navigation from query params
    if st.query_params.get('page'):
        page = st.query_params.get('page')
        if page in ['dashboard', 'sales', 'sales_orders', 'my_sales', 'users', 'settings']:
            st.session_state.current_page = page
        # Handle action
        if st.query_params.get('action'):
            st.session_state.page_action = st.query_params.get('action')
    
    if not st.session_state.logged_in:
        render_login()
        return
    
    user = st.session_state.current_user
    is_admin = user['role'] == 'admin'
    
    # Render the SPAR UI
    render_spar_nav()
    render_spar_sidebar()
    
    # Render the appropriate page
    page = st.session_state.current_page
    
    if page == 'dashboard':
        render_dashboard()
    elif page == 'sales':
        render_sales_form()
    elif page == 'sales_orders':
        render_sales_orders()
    elif page == 'my_sales':
        render_my_sales()
    elif page == 'users' and is_admin:
        render_users()
    elif page == 'settings' and is_admin:
        render_settings()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
