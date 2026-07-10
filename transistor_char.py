import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(page_title="Transistor Lab", layout="wide")

# CSS Styling for Blue/Cream Aesthetic
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #E6F3FF 0%, #FFFDD0 100%); }
        .stButton>button { width: 100%; border-radius: 5px; }
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

    # --- Main Interface ---
    tab1, tab2, tab3 = st.tabs(["📚 Basics", "📈 Simulation", "📝 Exercise"])

    with tab1:
        st.header("Practical: Common Emitter Characteristics")
        st.write("Understand how the Base Current ($I_B$) controls the Base-Emitter Voltage ($V_{BE}$).")
        # 

[Image of Common Emitter transistor circuit diagram]


    with tab2:
        st.header("Data Logger")
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Select $I_B$ (µA)")
            # Using buttons for 0 to 18 microampere selection
            selected_ib = None
            cols = st.columns(3)
            for i in range(19):
                if cols[i % 3].button(f"{i} µA"):
                    selected_ib = i
            
            if selected_ib is not None:
                # Calculate VBE based on inverse Shockley (logarithmic relationship)
                vt = 0.026
                is_val = 1e-12
                v_be = vt * np.log((selected_ib * 1e-6 / is_val) + 1)
                
                if st.button("Log this value"):
                    st.session_state.data.append({"IB (µA)": selected_ib, "VBE (V)": round(v_be, 3)})
                    st.success(f"Logged: {selected_ib} µA at {round(v_be, 3)} V")

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
        
        user_answers = {}
        for i, (q, options) in enumerate(questions):
            user_answers[f"q{i}"] = st.radio(f"{i+1}. {q}", options)
        
        if st.button("Submit Exercise"):
            st.write("### Submission Summary")
            st.write(f"Results for {st.session_state.matric} have been processed.")
            # Logic for email submission would be triggered here
