import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="EquiWork AI", layout="wide")

st.title("🤖 EquiWork AI: Agentic Workload Balancer")

# --- Sidebar: Controls ---
with st.sidebar:
    st.header("🛠️ Admin & Simulation")
    
    if st.button("♻️ Reset Demo Data", use_container_width=True):
        requests.post(f"{API_URL}/reset")
        st.success("Demo reset!")
        st.rerun()

    if st.button("📥 Sync Jira Tickets", use_container_width=True):
        res = requests.post(f"{API_URL}/sync/jira")
        st.info(f"Imported {res.json()['new_tasks']} new tasks.")
        st.rerun()

    st.divider()
    st.header("🤖 Agent Controls")
    if st.button("🚀 Run Analysis Agent", type="primary", use_container_width=True):
        with st.spinner("Analyzing team capacity..."):
            res = requests.post(f"{API_URL}/agent/run")
            st.success(f"Agent result: {res.json()['status']}")
            st.rerun()

# --- Section 1: Team Dashboard ---
st.subheader("📊 Team Load Scores")

try:
    employees = requests.get(f"{API_URL}/team").json()
    cols = st.columns(len(employees))
    
    for idx, emp in enumerate(employees):
        with cols[idx]:
            # Dynamic coloring based on status
            color = "green"
            if emp['status'] == "Red": color = "red"
            elif emp['status'] == "Yellow": color = "orange"
            
            st.markdown(f"### :{color}[{emp['name']}]")
            st.metric("Score", f"{emp['load_score']}/100")
            
            # Progress bar for visual impact
            st.progress(emp['load_score'] / 100)
            
            # Show skills tags
            st.write(f"**Skills:** {', '.join(emp['skills'])}")

except Exception:
    st.error("Backend offline. Run `python -m uvicorn app.main:app` in backend folder.")

st.divider()

# --- Section 2: Agent Proposals ---
st.subheader("⚡ Agent Proposals (Human-in-the-Loop)")

interventions = requests.get(f"{API_URL}/agent/interventions").json()

if not interventions:
    st.info("No active interventions. Team is currently balanced.")
else:
    for i in interventions:
        with st.container(border=True):
            st.warning(f"⚠️ **PROPOSAL:** {i['description']}")
            c1, c2 = st.columns(2)
            if c1.button("✅ Approve", key=f"app_{i['id']}"):
                requests.post(f"{API_URL}/agent/approve/{i['id']}")
                st.rerun()
            if c2.button("❌ Dismiss", key=f"dis_{i['id']}"):
                requests.post(f"{API_URL}/agent/dismiss/{i['id']}")
                st.rerun()