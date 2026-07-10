import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Transistor Lab", layout="wide")

st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #E6F3FF 0%, #FFFDD0 100%); }
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'data' not in st.session_state: st.session_state.data = []

# --- Authentication ---
if not st.session_state.logged_in:
    st.title("🎛️ Transistor Characteristics Lab")
    matric = st.text_input("Enter Matric Number")
    if st.button("Access Lab"):
        st.session_state.matric = matric
        st.session_state.logged_in = True
        st.rerun()
else:
    st.sidebar.write(f"Matric: {st.session_state.matric}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    tab1, tab2, tab3 = st.tabs(["Components", "Simulation", "Exercise"])

    with tab1:
        st.header("Hardware Components")
        st.write("- **NPN Transistor (Common Emitter Configuration)**")
        st.write("- **Variable DC Power Supply (VBE)**")
        st.write("- **Microammeter (Base Current IB)**")
        st.write("- **Voltmeter (Base-Emitter Voltage VBE)**")
        

    with tab2:
        st.header("Simulation Bench")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            ib_select = st.select_slider("Set IB (µA)", options=range(0, 19))
            
            # Physics Calculation
            vt = 0.026
            is_val = 1e-12
            v_be = vt * np.log(((ib_select * 1e-6) / is_val) + 1)
            
            st.metric("VBE Output (V)", f"{round(v_be, 3)} V")
            
            if st.button("Log Reading"):
                st.session_state.data.append({"IB (µA)": ib_select, "VBE (V)": round(v_be, 3)})
                st.success("Reading Logged")

        with col2:
            if st.session_state.data:
                df = pd.DataFrame(st.session_state.data)
                st.dataframe(df.sort_values("IB (µA)"))
                st.line_chart(df.sort_values("IB (µA)").set_index("IB (µA)"))

    with tab3:
        st.header("Exercise")
        q_data = [
            ("The input characteristics graph plots:", ["IB vs VBE", "IC vs VBE", "IB vs VCE", "IC vs IB"]),
            ("In CE configuration, the input is applied between:", ["Base & Emitter", "Collector & Emitter", "Base & Collector", "None"]),
            ("The value of thermal voltage (VT) at 300K is approximately:", ["26mV", "10mV", "50mV", "100mV"]),
            ("Which parameter is controlled by the power supply to adjust IB?", ["VBE", "VCE", "IC", "IE"]),
            ("The input characteristics of a CE transistor behave like:", ["Forward biased PN junction", "Reverse biased PN junction", "Pure resistor", "Open circuit"])
        ]
        
        for i, (q, options) in enumerate(q_data):
            st.radio(f"{i+1}. {q}", options, key=f"q{i}")
            
        if st.button("Submit Exercises"):
            st.success("Data and exercise results forwarded to lecturer.")
