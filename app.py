import streamlit as st
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import os
import json

# ---------- PAGE ----------
st.set_page_config(page_title="Water Dashboard", layout="wide")

# ---------- USER SYSTEM ----------
USER_FILE = "users.json"

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# ---------- LOGIN ----------
def login_page():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        users = load_users()
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    if st.button("Signup"):
        st.session_state.page = "signup"
        st.rerun()

# ---------- SIGNUP ----------
def signup_page():
    st.title("📝 Signup")

    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")

    if st.button("Create Account"):
        users = load_users()
        if new_user in users:
            st.warning("User already exists")
        else:
            users[new_user] = new_pass
            save_users(users)
            st.success("Account created successfully")

    if st.button("Back to Login"):
        st.session_state.page = "login"
        st.rerun()

# ---------- DASHBOARD ----------
def dashboard():

    # ---------- LOAD FILES SAFELY ----------
    if not os.path.exists("model.pkl") or not os.path.exists("water_data_big.csv"):
        st.error("❌ Model or dataset missing. Run generate_data.py and model.py first.")
        return

    model = pickle.load(open("model.pkl", "rb"))
    df = pd.read_csv("water_data_big.csv")

    # ---------- FIX COLUMNS ----------
    if "zone_name" not in df.columns and "zone" in df.columns:
        df["zone_name"] = df["zone"]

    # ---------- HEADER ----------
    colA, colB = st.columns([8,1])
    with colA:
        st.title("💧 Water Demand Prediction Dashboard")
    with colB:
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.rerun()

    # ---------- SIDEBAR ----------
    st.sidebar.header("Input Parameters")

    zone = st.sidebar.selectbox("Zone", ["Residential_A","Commercial_B","Industrial_C"])

    zone_map = {
        "Residential_A":0,
        "Commercial_B":1,
        "Industrial_C":2
    }

    population = st.sidebar.number_input("Population",1000,10000)
    temperature = st.sidebar.slider("Temperature",10,45)
    rainfall = st.sidebar.slider("Rainfall",0,100)
    is_weekend = st.sidebar.selectbox("Weekend",[0,1])
    is_festival = st.sidebar.selectbox("Festival",[0,1])
    day = st.sidebar.slider("Day",1,31)
    month = st.sidebar.slider("Month",1,12)

    # ---------- PREDICTION ----------
    if st.sidebar.button("Predict"):
        data = [[
            zone_map[zone],
            population,
            temperature,
            rainfall,
            is_weekend,
            is_festival,
            day,
            month
        ]]

        pred = model.predict(data)[0]

        c1, c2, c3 = st.columns(3)

        c1.metric("Predicted Demand", f"{int(pred)} L")

        if pred < 120000:
            c2.metric("Category","Low")
        elif pred < 150000:
            c2.metric("Category","Medium")
        else:
            c2.metric("Category","High")

        if temperature > 35:
            c3.metric("Insight","Hot ↑ Demand")
        elif rainfall > 0:
            c3.metric("Insight","Rain ↓ Demand")
        else:
            c3.metric("Insight","Normal")

    # ---------- DATA CLEAN ----------
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors='coerce')

    # ---------- GRAPHS ----------
    col1, col2 = st.columns(2)

    # ---- GRAPH 1 ----
    with col1:
        st.subheader("📈 Water Usage Trend")

        if not df.empty and "zone_name" in df.columns:
            zone_sel = st.selectbox("Select Zone", df["zone_name"].unique())
            filtered = df[df["zone_name"] == zone_sel]

            if not filtered.empty and "date" in filtered.columns and "water_supply" in filtered.columns:
                fig = plt.figure()
                plt.plot(filtered["date"], filtered["water_supply"])
                plt.xticks(rotation=45)
                plt.xlabel("Date")
                plt.ylabel("Water Supply")
                st.pyplot(fig)
            else:
                st.warning("No data available for selected zone")
        else:
            st.warning("Dataset is empty")

    # ---- GRAPH 2 ----
    with col2:
        st.subheader("📊 Average Demand by Zone")

        if not df.empty and "zone_name" in df.columns and "water_supply" in df.columns:
            fig2 = plt.figure()
            df.groupby("zone_name")["water_supply"].mean().plot(kind="bar")
            plt.xlabel("Zone")
            plt.ylabel("Average Supply")
            st.pyplot(fig2)
        else:
            st.warning("No valid data available for plotting")

# ---------- ROUTING ----------
if not st.session_state.logged_in:
    if st.session_state.page == "login":
        login_page()
    else:
        signup_page()
else:
    dashboard()