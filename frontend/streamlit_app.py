import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="EquiWork AI", layout="wide")

st.title("🤖 EquiWork AI: Agentic Workload Balancer")

# --- Sidebar: Controls ---
with st.sidebar:
    st.header("Agent Controls")
    if st.button("🚀 Run Analysis Agent"):
        res = requests.post(f"{API_URL}/agent/run")
        st.success(f"Agent finished: {res.json()['status']}")

# --- Section 1: Team Dashboard ---
st.subheader("📊 Team Load Scores")

# Fetch latest data
try:
    employees = requests.get(f"{API_URL}/team").json()
    
    cols = st.columns(len(employees))
    for idx, emp in enumerate(employees):
        with cols[idx]:
            color = "green"
            if emp['status'] == "Red": color = "red"
            if emp['status'] == "Yellow": color = "orange"
            
            st.markdown(f"### :{color}[{emp['name']}]")
            st.metric("Load Score", f"{emp['load_score']}/100")
            st.caption(f"Status: {emp['status']}")

except Exception as e:
    st.error("Backend not running. Run: `python backend/app/main.py`")

st.divider()

# --- Section 2: Agent Interventions ---
st.subheader("⚡ Agent Proposals (Human-in-the-Loop)")

interventions = requests.get(f"{API_URL}/agent/interventions").json()

if not interventions:
    st.info("No active interventions. Team is balanced or Agent hasn't run.")
else:
    for i in interventions:
        with st.container():
            st.warning(f"⚠️ PROPOSAL: {i['description']}")
            c1, c2 = st.columns(2)
            if c1.button("✅ Approve", key=f"app_{i['id']}"):
                requests.post(f"{API_URL}/agent/approve/{i['id']}")
                st.rerun()
            if c2.button("❌ Dismiss", key=f"dis_{i['id']}"):
                requests.post(f"{API_URL}/agent/dismiss/{i['id']}")
                st.rerun()