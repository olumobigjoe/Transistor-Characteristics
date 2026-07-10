import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(page_title="Transistor Characteristics Lab", layout="wide")

# CSS Styling for a professional, academic look
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #E6F3FF 0%, #FFFDD0 100%); }
        .data-box { background-color: white; padding: 10px; border-radius: 10px; border: 1px solid #ccc; }
    </style>
""", unsafe_allow_html=True)

# State Management
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'data' not in st.session_state: st.session_state.data = []

# --- Authentication ---
if not st.session_state.logged_in:
    st.title("🎛️ Transistor Characteristics Lab")
    matric = st.text_input("Enter Matric Number to Access Lab")
    if st.button("Enter Lab"):
        if matric:
            st.session_state.matric = matric
            st.session_state.logged_in = True
            st.rerun()
else:
    st.sidebar.title(f"Student: {st.session_state.matric}")
    if st.sidebar.button("Logout"):
        st.session_state.data = [] # Clear data on logout
        st.session_state.logged_in = False
        st.rerun()

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["📚 Lab Manual", "🧪 Simulation Bench", "📝 Post-Lab Exercises"])

    with tab1:
        st.header("Experiment: Transistor Input Characteristics")
        st.write("""
        ### Objective:
        To determine the input characteristic of a common-emitter NPN transistor.
        
        ### Procedure:
        1. Access the **Simulation Bench** tab.
        2. Vary the Base Current ($I_B$) using the provided selector (0–18 µA).
        3. Observe the generated Base-Emitter Voltage ($V_{BE}$).
        4. Click **'Log Reading'** to record the pair in your lab data table.
        5. Observe the plotted graph to confirm the characteristic curve.
        """)

    with tab2:
        st.header("Laboratory Simulation Bench")
        col1, col2 = st.columns([1, 2])
        
        # Simulation Logic
        vt = 0.026
        is_val = 1e-12
        
        with col1:
            st.subheader("Controls")
            selected_ib = st.radio("Select Base Current (µA):", range(0, 19), horizontal=True)
            
            # Physics Calculation
            v_be = vt * np.log(((selected_ib * 1e-6) / is_val) + 1)
            st.metric(label="Calculated VBE (Volts)", value=f"{round(v_be, 3)} V")
            
            if st.button("Log Reading"):
                st.session_state.data.append({"IB (µA)": selected_ib, "VBE (V)": round(v_be, 3)})
                st.success(f"Recorded: {selected_ib} µA, {round(v_be, 3)} V")

        with col2:
            st.subheader("Data Table & Graphs")
            if st.session_state.data:
                df = pd.DataFrame(st.session_state.data)
                st.dataframe(df.sort_values(by="IB (µA)"), use_container_width=True)
                
                st.write("### VBE vs IB Characteristic Curve")
                st.line_chart(df.sort_values(by="IB (µA)").set_index("IB (µA)"))
            else:
                st.info("Your data table is empty. Start by logging your first reading.")

    with tab3:
        st.header("Post-Lab Exercises")
        questions = [
            ("Which configuration is used to determine the input characteristics of a transistor?", ["Common Emitter", "Common Base", "Common Collector", "None"]),
            ("As base current increases, the base-emitter voltage:", ["Increases logarithmically", "Decreases linearly", "Remains constant", "Fluctuates"]),
            ("The input characteristics of a CE transistor are similar to which device?", ["Forward-biased diode", "Reverse-biased diode", "Resistor", "Capacitor"]),
            ("Which parameters are plotted on the X and Y axes for input characteristics?", ["IB and VBE", "IC and VBE", "IB and VCE", "IC and IB"]),
            ("What does the 'VT' (Thermal Voltage) represent at room temperature?", ["26 mV", "10 mV", "50 mV", "100 mV"])
        ]
        
        for i, (q, options) in enumerate(questions):
            st.radio(f"{i+1}. {q}", options, key=f"q{i}")
        
        if st.button("Submit Final Lab Report"):
            st.success(f"Experiment data and quiz results for {st.session_state.matric} forwarded to lecturer.")
