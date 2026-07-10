import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(page_title="Transistor Lab", layout="wide")

# CSS Styling
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #E6F3FF 0%, #FFFDD0 100%); }
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
        st.session_state.matric = matric
        st.session_state.logged_in = True
        st.rerun()
else:
    st.sidebar.title(f"Student: {st.session_state.matric}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["📚 Basics", "📈 Simulation", "📝 Exercise"])

    with tab1:
        st.header("Practical: Common Emitter Characteristics")
        st.write("Understand how the Base Current (IB) controls the Base-Emitter Voltage (VBE).")
        # 

    with tab2:
        st.header("Data Logger")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Select IB (µA)")
            # Create buttons for 0 to 18
            for i in range(0, 19, 3):
                row = st.columns(3)
                for j in range(3):
                    if i + j <= 18:
                        if row[j].button(f"{i + j} µA"):
                            # Calculate VBE
                            vt = 0.026
                            is_val = 1e-12
                            v_be = vt * np.log(((i + j) * 1e-6 / is_val) + 1)
                            st.session_state.data.append({"IB (µA)": i + j, "VBE (V)": round(v_be, 3)})
                            st.rerun()

        with col2:
            if st.session_state.data:
                df = pd.DataFrame(st.session_state.data)
                st.write("### Logged Data")
                st.dataframe(df)
                st.write("### Graphical Display")
                st.line_chart(df.set_index("IB (µA)"))
            else:
                st.info("Select a current value from the left to start logging.")

    with tab3:
        st.header("Post-Lab Exercises")
        questions = [
            ("What is the primary function of a CE transistor?", ["Amplifier", "Resistor", "Capacitor", "Inductor"]),
            ("The input characteristic plots which two parameters?", ["IB vs VBE", "IC vs VBE", "IB vs VCE", "IC vs VCE"]),
            ("What happens to VBE as IB increases?", ["Increases", "Decreases", "Stays Constant", "Becomes Zero"]),
            ("In CE mode, the emitter is:", ["Common to both input/output", "Only input", "Only output", "Disconnected"]),
            ("What is the approximate value of VT at 300K?", ["26mV", "10mV", "50mV", "100mV"])
        ]
        
        for i, (q, options) in enumerate(questions):
            st.radio(f"{i+1}. {q}", options, key=f"q{i}")
        
        if st.button("Submit Exercise"):
            st.success(f"Results for {st.session_state.matric} have been submitted.")
