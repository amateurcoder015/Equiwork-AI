import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="EquiWork AI", layout="wide")

st.title(" EquiWork AI: Agentic Workload Balancer")

# --- Sidebar: Controls ---
with st.sidebar:
    st.header("Admin & Simulation")
    
    if st.button("Reset Demo Data", use_container_width=True):
        try:
            requests.post(f"{API_URL}/reset")
            st.success("Demo reset!")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to connect: {e}")

    if st.button("Sync Jira Tickets", use_container_width=True):
        try:
            res = requests.post(f"{API_URL}/sync/jira")
            if res.status_code == 200:
                st.info(f"Imported {res.json().get('new_tasks', 0)} new tasks.")
                st.rerun()
            else:
                st.error("Sync failed.")
        except Exception as e:
            st.error(f"Error: {e}")

    st.divider()
    st.header("Agent Controls")
    if st.button("Run Analysis Agent", type="primary", use_container_width=True):
        with st.spinner("Analyzing team capacity..."):
            try:
                res = requests.post(f"{API_URL}/agent/run")
                if res.status_code == 200:
                    try:
                        data = res.json()
                        st.success(f"Agent result: {data.get('status')}")
                        if data.get('actions_proposed', 0) > 0:
                            st.rerun()
                    except requests.exceptions.JSONDecodeError:
                        st.error("Backend Error: Received invalid response.")
                else:
                    st.error(f"Server Error {res.status_code}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# --- Section 1: Team Dashboard ---
st.subheader("Team Load Scores")

try:
    # 1. Fetch both Team and Tasks data
    employees = requests.get(f"{API_URL}/team").json()
    all_tasks = requests.get(f"{API_URL}/tasks").json()
    
    cols = st.columns(len(employees))
    
    for idx, emp in enumerate(employees):
        with cols[idx]:
            # Status Color Logic
            color = "green"
            if emp['status'] == "Red": color = "red"
            elif emp['status'] == "Yellow": color = "orange"
            
            # Employee Header
            st.markdown(f"### :{color}[{emp['name']}]")
            st.metric("Score", f"{emp['load_score']}/100")
            st.progress(emp['load_score'] / 100)
            
            # Skills Tags
            st.caption(f"{', '.join(emp['skills'])}")

            # --- NEW: Task Visibility Layer ---
            # Filter tasks belonging to this employee
            my_tasks = [t for t in all_tasks if t['assignee_id'] == emp['id']]
            
            if my_tasks:
                with st.expander(f"View {len(my_tasks)} Active Tasks", expanded=True):
                    for t in my_tasks:
                        # Visual cues for task type
                        type_icon = "🔥" if t['type'] == 'maintenance' else "🌱"
                        complexity_color = "red" if t['complexity'] > 7 else "blue"
                        
                        st.markdown(f"**{type_icon} {t['title']}**")
                        st.caption(f"Complexity: :{complexity_color}[{t['complexity']}/10] • Vis: {t['visibility']}")
                        st.markdown(f"_{t.get('description', 'No description')}_")
                        st.divider()
            else:
                st.info("No active tasks", icon="💤")

except Exception as e:
    st.error(f"Backend offline or connection error: {e}")
    st.code("Run: python -m uvicorn app.main:app --reload")

st.divider()

# --- Section 2: Agent Proposals ---
st.subheader("⚡ Agent Proposals (Human-in-the-Loop)")

try:
    interventions = requests.get(f"{API_URL}/agent/interventions").json()

    if not interventions:
        st.info("No active interventions. Team is currently balanced.")
    else:
        for i in interventions:
            with st.container(border=True):
                st.warning(f"⚠️ **PROPOSAL:** {i['description']}")
                
                # Show specific details of the move
                st.markdown(f"**Action:** Reassign Task `{i.get('task_id', 'Unknown')}`")
                
                c1, c2 = st.columns(2)
                if c1.button("✅ Approve", key=f"app_{i['id']}"):
                    requests.post(f"{API_URL}/agent/approve/{i['id']}")
                    st.rerun()
                if c2.button("❌ Dismiss", key=f"dis_{i['id']}"):
                    requests.post(f"{API_URL}/agent/dismiss/{i['id']}")
                    st.rerun()
except Exception:
    st.write("Waiting for agent data...")