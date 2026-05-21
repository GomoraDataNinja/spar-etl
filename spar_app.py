import streamlit as st
import pandas as pd
import json
import hashlib
import re
import time
from pathlib import Path
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Tengai",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide default Streamlit elements
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            background: linear-gradient(135deg, #E8F0FE 0%, #FFFFFF 100%);
        }
        .stButton > button {
            background-color: #E3000F;
            color: white;
            border: none;
            padding: 0.6rem;
            border-radius: 12px;
            width: 100%;
            font-weight: 600;
        }
        .stTextInput > div > div > input {
            border-radius: 12px;
            padding: 0.6rem;
        }
    </style>
""", unsafe_allow_html=True)

# User storage
USERS_FILE = Path("users.json")

def get_users():
    if USERS_FILE.exists():
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user(email, name, username, password):
    users = get_users()
    users[email] = {
        'name': name,
        'email': email,
        'username': username,
        'password': hashlib.sha256(password.encode()).hexdigest(),
        'role': 'admin' if len(users) == 0 else 'user',
        'created': datetime.now().isoformat()
    }
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    return True

def login_user(username, password):
    users = get_users()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    for email, user in users.items():
        if user['username'] == username or email == username:
            if user['password'] == hashed:
                st.session_state.logged_in = True
                st.session_state.user = user
                return True
    return False

def register_user(name, username, email, password):
    users = get_users()
    
    if email in users:
        return False, "Email already registered"
    
    for u in users.values():
        if u['username'] == username:
            return False, "Username already taken"
    
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email"
    
    if len(password) < 6:
        return False, "Password must be 6+ characters"
    
    save_user(email, name, username, password)
    return True, "Account created! Please sign in."

# Initialize session
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None
    st.session_state.show_register = False

# Create default admin if no users
if len(get_users()) == 0:
    save_user("admin@tengai.com", "Administrator", "admin", "Admin@123")

# ============================================
# LOGIN SCREEN - ONE BOX WITH BOTH OPTIONS
# ============================================

if not st.session_state.logged_in:
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; padding-top: 3rem;">
            <div style="background: white; border-radius: 24px; padding: 2rem; width: 100%; max-width: 400px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #E5E7EB;">
                <h1 style="color: #E3000F; font-size: 1.8rem; text-align: center; margin-bottom: 0.5rem;">Tengai</h1>
                <p style="color: #6B7280; font-size: 0.8rem; text-align: center; margin-bottom: 0.2rem;">Welcome to Tengai, Your</p>
                <p style="color: #6B7280; font-size: 0.8rem; text-align: center; margin-bottom: 0.8rem;">AI-Rewards Integrated App</p>
                <div style="text-align: center; margin-bottom: 1.5rem;">
                    <span style="background: #F9FAFB; padding: 0.2rem 0.8rem; border-radius: 30px; font-size: 0.7rem;">● Version 3.3.0 - Production</span>
                </div>
    """, unsafe_allow_html=True)
    
    # Toggle buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign In", use_container_width=True, type="primary" if not st.session_state.show_register else "secondary"):
            st.session_state.show_register = False
            st.rerun()
    with col2:
        if st.button("Create Account", use_container_width=True, type="primary" if st.session_state.show_register else "secondary"):
            st.session_state.show_register = True
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if not st.session_state.show_register:
        # SIGN IN FORM
        st.markdown('<h2 style="color: #E3000F; font-size: 1rem; text-align: center; margin-bottom: 1rem;">Sign In</h2>', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown('<p style="font-size: 0.75rem; font-weight: 500;">Name</p>', unsafe_allow_html=True)
            username = st.text_input("", placeholder="Enter your username or email", label_visibility="collapsed")
            
            st.markdown('<p style="font-size: 0.75rem; font-weight: 500;">Password</p>', unsafe_allow_html=True)
            password = st.text_input("", type="password", placeholder="Enter your password", label_visibility="collapsed")
            
            submitted = st.form_submit_button("Sign In", use_container_width=True)
            
            if submitted:
                if username and password:
                    if login_user(username, password):
                        st.success("Login successful!")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.error("Please enter name and password")
    else:
        # CREATE ACCOUNT FORM
        st.markdown('<h2 style="color: #E3000F; font-size: 1rem; text-align: center; margin-bottom: 1rem;">Create Account</h2>', unsafe_allow_html=True)
        
        with st.form("register_form", clear_on_submit=False):
            st.markdown('<p style="font-size: 0.75rem; font-weight: 500;">Full Name</p>', unsafe_allow_html=True)
            name = st.text_input("", placeholder="Enter your full name", label_visibility="collapsed")
            
            st.markdown('<p style="font-size: 0.75rem; font-weight: 500;">Username</p>', unsafe_allow_html=True)
            username = st.text_input("", placeholder="Choose a username", label_visibility="collapsed", key="reg_username")
            
            st.markdown('<p style="font-size: 0.75rem; font-weight: 500;">Email</p>', unsafe_allow_html=True)
            email = st.text_input("", placeholder="your@email.com", label_visibility="collapsed", key="reg_email")
            
            st.markdown('<p style="font-size: 0.75rem; font-weight: 500;">Password</p>', unsafe_allow_html=True)
            password = st.text_input("", type="password", placeholder="Min 6 characters", label_visibility="collapsed", key="reg_password")
            
            st.markdown('<p style="font-size: 0.75rem; font-weight: 500;">Confirm Password</p>', unsafe_allow_html=True)
            confirm = st.text_input("", type="password", placeholder="Confirm your password", label_visibility="collapsed")
            
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                if not all([name, username, email, password]):
                    st.error("Please fill all fields")
                elif password != confirm:
                    st.error("Passwords do not match")
                else:
                    success, msg = register_user(name, username, email, password)
                    if success:
                        st.success(msg)
                        st.session_state.show_register = False
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

# ============================================
# MAIN APP AFTER LOGIN
# ============================================

else:
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #E3000F 0%, #007A3D 100%); padding: 1rem 1.5rem; border-radius: 16px; margin-bottom: 1.5rem;">
            <h1 style="margin: 0; font-size: 1.2rem; color: white;">🛒 Tengai - SPAR Sales System</h1>
            <p style="margin: 0.2rem 0 0 0; opacity: 0.9; font-size: 0.7rem; color: white;">Welcome, {st.session_state.user['name']} ({st.session_state.user['role'].upper()})</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Sign Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
    
    st.success("✅ You are logged in!")
    st.info("Sales entry form will be added here...")
