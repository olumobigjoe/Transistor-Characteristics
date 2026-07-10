import streamlit as st
import pandas as pd
import numpy as np
import smtplib
from email.message import EmailMessage

# 1. Page Configuration & Styling
st.set_page_config(page_title="Transistor Lab Simulator", layout="wide")
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #E6F3FF 0%, #FFFDD0 100%); }
    </style>
""", unsafe_allow_html=True)

# 2. Initialization
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'data' not in st.session_state: st.session_state.data = []

# 3. Authentication
if not st.session_state.logged_in:
    st.title("Physics Lab Login")
    matric = st.text_input("Enter Matric Number")
    if st.button("Login"):
        st.session_state.matric = matric
        st.session_state.logged_in = True
        st.rerun()
else:
    st.sidebar.write(f"Student: {st.session_state.matric}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("Common Emitter Transistor Characteristics")
    tab1, tab2, tab3 = st.tabs(["Basics", "Simulation", "Exercise"])

    with tab1:
        st.header("Practical Basics")
        st.write("The Common Emitter (CE) configuration is the most widely used transistor circuit.")
        # 

    with tab2:
        st.header("Simulation Lab")
        v_be = st.slider("Adjust VBE (Volts)", 0.0, 0.9, 0.5, 0.01)
        # Simplified simulation: Ib = Is * (exp(Vbe/Vt) - 1)
        i_b = (1e-12 * (np.exp(v_be / 0.026) - 1)) * 1e6 
        st.metric("Base Current (µA)", f"{i_b:.2f}")
        
        if st.button("Log Data"):
            st.session_state.data.append({"VBE": v_be, "IB": i_b})
            st.success("Data Point Logged")
        
        if st.session_state.data:
            df = pd.DataFrame(st.session_state.data)
            st.line_chart(df.set_index("VBE"))

    with tab3:
        st.header("Final Exercise")
        answers = {
            "q1": st.radio("1. What is the main use of the CE configuration?", ["Amplification", "Switching", "Both"]),
            "q2": st.text_input("2. What is the value of Vt at room temperature?"),
            # ... add remaining 3 questions
        }
        if st.button("Submit Performance"):
            # Placeholder for email logic
            st.write(f"Results for {st.session_state.matric} sent to Lecturer.")
            # In production, use smtplib here to send st.session_state.data + answers