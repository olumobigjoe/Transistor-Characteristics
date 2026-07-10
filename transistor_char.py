"""
Common Emitter Transistor Characteristics - Virtual Lab
=========================================================
An interactive Streamlit simulator for physics/electronics students to
determine the Input, Current Transfer and Voltage Transfer characteristics
of a Common-Emitter (CE) connected BJT.

Run with:
    streamlit run app.py
"""

import os
import re
import math
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# =========================================================================
# PAGE CONFIG (must be first Streamlit call)
# =========================================================================
st.set_page_config(
    page_title="CE Transistor Characteristics Lab",
    page_icon="🔌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================================
# CONSTANTS / TRANSISTOR MODEL PARAMETERS
# =========================================================================
VT = 0.02585        # Thermal voltage at ~300K (V)
IS = 1e-14          # Reverse saturation current (A) - typical small-signal NPN
BETA_DEFAULT = 100  # DC current gain (hFE)
VCE_SAT = 0.2       # Collector-emitter saturation voltage (V)

DATA_DIR = "lab_data"
RESULTS_FILE = os.path.join(DATA_DIR, "student_results.csv")
os.makedirs(DATA_DIR, exist_ok=True)

EXERCISE_QUESTIONS = [
    {
        "q": "1. In the Common-Emitter (CE) configuration, which terminal is common to both the input and output circuits?",
        "options": ["Base", "Emitter", "Collector", "None of the terminals"],
        "answer": "Emitter",
    },
    {
        "q": "2. The Input Characteristic of a CE transistor is a plot of:",
        "options": [
            "I_C against V_CE at constant I_B",
            "I_B against V_BE at constant V_CE",
            "I_C against I_B at constant V_CE",
            "V_CE against V_BE at constant I_B",
        ],
        "answer": "I_B against V_BE at constant V_CE",
    },
    {
        "q": "3. For a silicon transistor operating in the active region, the base-emitter voltage (V_BE) is typically close to:",
        "options": ["0.1 - 0.2 V", "0.6 - 0.7 V", "1.5 - 2.0 V", "5.0 V"],
        "answer": "0.6 - 0.7 V",
    },
    {
        "q": "4. A transistor enters SATURATION when:",
        "options": [
            "V_CE falls to a very low value (close to V_CE(sat)) as I_B keeps increasing",
            "I_B is reduced to zero",
            "V_BE becomes negative",
            "I_C becomes exactly equal to I_B",
        ],
        "answer": "V_CE falls to a very low value (close to V_CE(sat)) as I_B keeps increasing",
    },
    {
        "q": "5. The Current Transfer Characteristic relates which two quantities, and gives which important parameter?",
        "options": [
            "V_BE and V_CE; gives the saturation voltage",
            "I_B and V_BE; gives the input resistance",
            "I_C and I_B; gives the current gain (beta / h_FE)",
            "I_C and V_CE; gives the output resistance",
        ],
        "answer": "I_C and I_B; gives the current gain (beta / h_FE)",
    },
]

# =========================================================================
# CUSTOM STYLING - Blue & Cream theme
# =========================================================================
def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(160deg, #dbe9f6 0%, #eef2e2 45%, #fbf4e2 100%);
        }
        .lab-card {
            background: rgba(255, 255, 255, 0.88);
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            box-shadow: 0 4px 18px rgba(30, 58, 95, 0.12);
            border: 1px solid rgba(30, 58, 95, 0.08);
            margin-bottom: 1rem;
        }
        h1, h2, h3 {
            color: #1b3a57 !important;
        }
        .top-banner {
            background: linear-gradient(90deg, #1b3a57 0%, #2b6cb0 100%);
            padding: 1.1rem 1.6rem;
            border-radius: 14px;
            color: #fdf6e3;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 14px rgba(27,58,87,0.25);
        }
        .top-banner h1 {
            color: #fdf6e3 !important;
            margin: 0;
            font-size: 1.6rem;
        }
        .top-banner span {
            color: #eaf2fb;
            font-size: 0.95rem;
        }
        div.stButton > button {
            background-color: #2b6cb0;
            color: #fdf6e3;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1.1rem;
            font-weight: 600;
        }
        div.stButton > button:hover {
            background-color: #1b3a57;
            color: #fdf6e3;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: rgba(255,255,255,0.6);
            border-radius: 10px 10px 0 0;
            padding: 8px 18px;
            font-weight: 600;
            color: #1b3a57;
        }
        .stTabs [aria-selected="true"] {
            background-color: #2b6cb0 !important;
            color: #fdf6e3 !important;
        }
        .correct-badge {color: #256029; font-weight: 700;}
        .wrong-badge {color: #a12727; font-weight: 700;}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================================
# SESSION STATE INITIALISATION
# =========================================================================
def init_state():
    defaults = {
        "logged_in": False,
        "matric": "",
        "student_name": "",
        "readings": [],          # list of dicts: IB, VBE, IC, VCE, region
        "vcc": 10.0,
        "rc_kohm": 1.0,
        "beta": BETA_DEFAULT,
        "exercise_answers": {},
        "exercise_submitted": False,
        "exercise_score": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# =========================================================================
# HELPER FUNCTIONS
# =========================================================================
def valid_matric_format(matric: str) -> bool:
    """Accepts common matric-number style formats, e.g. CSC/2020/1234,
    2019/12345EE, ENG-2021-045, etc. Just checks a sane format, no roster
    lookup is performed."""
    m = matric.strip()
    if len(m) < 4:
        return False
    if not re.fullmatch(r"[A-Za-z0-9/\-]+", m):
        return False
    if not any(ch.isdigit() for ch in m):
        return False
    return True


def compute_operating_point(ib_uA: float, vcc: float, rc_kohm: float, beta: float):
    """Given a base current (µA) set by the student, compute the
    corresponding V_BE (input characteristic), I_C (current transfer)
    and V_CE (voltage transfer), including saturation clamping."""
    ib = ib_uA * 1e-6          # A
    rc = rc_kohm * 1e3         # ohms

    ic_active = beta * ib
    vce_active = vcc - ic_active * rc

    if vce_active <= VCE_SAT:
        # Transistor driven into saturation
        vce = VCE_SAT
        ic = (vcc - VCE_SAT) / rc
        region = "Saturation"
    else:
        vce = vce_active
        ic = ic_active
        region = "Active"

    vbe = VT * math.log(max(ic, 1e-15) / IS) if ic > 0 else 0.0
    return vbe, ic, vce, region


def draw_ce_schematic():
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # VCC supply rail
    ax.plot([7, 7], [7, 6.3], color="#1b3a57", lw=2)
    ax.text(7.2, 7.1, "VCC", fontsize=10, color="#1b3a57")

    # RC resistor (zig-zag)
    zz_x = np.array([7, 7 - 0.15, 7 + 0.15, 7 - 0.15, 7 + 0.15, 7])
    zz_y = np.linspace(6.3, 5.2, 6)
    ax.plot(zz_x, zz_y, color="#1b3a57", lw=2)
    ax.text(7.3, 5.7, "RC", fontsize=10, color="#1b3a57")

    # Collector wire down to transistor
    ax.plot([7, 7], [5.2, 4.4], color="#1b3a57", lw=2)

    # Transistor body (circle)
    circ = plt.Circle((6.4, 3.6), 0.9, fill=False, color="#1b3a57", lw=2)
    ax.add_patch(circ)
    ax.plot([7, 6.6], [4.4, 3.9], color="#1b3a57", lw=2)   # collector lead
    ax.plot([6.6, 6.6], [3.9, 3.3], color="#1b3a57", lw=2.5)  # internal bar
    ax.plot([6.6, 7.1], [3.3, 2.8], color="#1b3a57", lw=2)   # emitter lead
    ax.annotate("", xy=(7.1, 2.8), xytext=(6.9, 3.0),
                arrowprops=dict(arrowstyle="->", color="#1b3a57", lw=1.5))
    ax.plot([7.1, 7.1], [2.8, 2.0], color="#1b3a57", lw=2)  # emitter to ground
    ax.text(7.3, 2.3, "E", fontsize=10, color="#1b3a57")
    ax.text(7.3, 4.1, "C", fontsize=10, color="#1b3a57")

    # Base lead + RB + VBB supply
    ax.plot([5.7, 6.6], [3.6, 3.6], color="#1b3a57", lw=2)
    ax.text(5.9, 3.75, "B", fontsize=10, color="#1b3a57")
    zzb_y = np.array([3.6, 3.6 - 0.15, 3.6 + 0.15, 3.6 - 0.15, 3.6 + 0.15, 3.6])
    zzb_x = np.linspace(5.7, 4.3, 6)
    ax.plot(zzb_x, zzb_y, color="#1b3a57", lw=2)
    ax.text(4.7, 3.85, "RB", fontsize=10, color="#1b3a57")
    ax.plot([4.3, 3.4], [3.6, 3.6], color="#1b3a57", lw=2)
    ax.plot([3.4, 3.4], [3.6, 4.6], color="#1b3a57", lw=2)
    ax.text(3.0, 4.7, "VBB\n(sets IB)", fontsize=9, color="#1b3a57", ha="center")

    # Ground symbols
    for gx, gy in [(3.4, 2.0), (7.1, 2.0)]:
        ax.plot([gx - 0.25, gx + 0.25], [gy, gy], color="#1b3a57", lw=2)
        ax.plot([gx - 0.15, gx + 0.15], [gy - 0.15, gy - 0.15], color="#1b3a57", lw=1.5)
        ax.plot([gx - 0.05, gx + 0.05], [gy - 0.3, gy - 0.3], color="#1b3a57", lw=1)
        ax.plot([gx, gx], [2.0, 3.05 if gx == 3.4 else 2.8], color="#1b3a57", lw=2)

    ax.text(6.4, 1.2, "NPN transistor in Common-Emitter configuration",
            fontsize=9, color="#1b3a57", ha="center", style="italic")

    fig.patch.set_alpha(0)
    return fig


def save_result_row(row: dict):
    file_exists = os.path.isfile(RESULTS_FILE)
    df_row = pd.DataFrame([row])
    df_row.to_csv(RESULTS_FILE, mode="a", header=not file_exists, index=False)


# =========================================================================
# LOGIN PAGE
# =========================================================================
def login_page():
    inject_css()
    st.markdown(
        """
        <div class="top-banner">
            <h1>🔌 Common-Emitter Transistor Characteristics — Virtual Lab</h1>
            <span>Physics / Electronics Department &middot; Student Access Portal</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown('<div class="lab-card">', unsafe_allow_html=True)
        st.subheader("🔐 Student Login")
        st.write("Please log in with your matric number to access the lab.")
        name = st.text_input("Full Name (optional)", placeholder="e.g. Ada Okafor")
        matric = st.text_input("Matric Number", placeholder="e.g. ENG/2021/0456")
        login_clicked = st.button("Log In", use_container_width=True)

        if login_clicked:
            if not valid_matric_format(matric):
                st.error(
                    "Please enter a valid matric number "
                    "(letters/numbers, at least 4 characters, must contain a digit)."
                )
            else:
                st.session_state.logged_in = True
                st.session_state.matric = matric.strip()
                st.session_state.student_name = name.strip()
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================================
# TAB 1 — LEARN THE BASICS
# =========================================================================
def learn_tab():
    st.markdown('<div class="lab-card">', unsafe_allow_html=True)
    st.header("📘 Learning the Basics")

    st.markdown(
        """
The **Common-Emitter (CE)** configuration is the most widely used transistor
connection because it provides good current, voltage and power gain. The
**emitter** terminal is common to both the input (base-emitter) and output
(collector-emitter) circuits.

#### Components used in this practical
| Component | Function |
|---|---|
| NPN Transistor | The device under test |
| Variable base supply (V_BB) | Varies the base-emitter voltage, which sets I_B |
| Variable collector supply (V_CC) | Supplies the collector circuit |
| Resistor R_B | Limits/sets the base current |
| Resistor R_C | Collector load resistor, converts I_C to a voltage |
| Microammeter | Measures base current, I_B (µA) |
| Milliammeter | Measures collector current, I_C (mA) |
| Voltmeters | Measure V_BE and V_CE |
        """
    )

    st.pyplot(draw_ce_schematic(), use_container_width=False)

    st.markdown(
        """
#### The three characteristics you will determine

**1. Input Characteristic** — a plot of base current *I_B* against
base-emitter voltage *V_BE*, at a constant *V_CE*. It resembles the
forward characteristic of a diode, and its slope gives the input
resistance of the transistor.

**2. Current Transfer Characteristic** — a plot of collector current
*I_C* against base current *I_B*. Its slope is the DC current gain,
**β (h_FE) = I_C / I_B**.

**3. Voltage Transfer Characteristic** — a plot of *V_CE* against *V_BE*.
As *V_BE* increases, *I_B* and hence *I_C* increase, causing the voltage
drop across *R_C* to increase and *V_CE* to fall — moving the transistor
from **cut-off → active → saturation**.

#### How this simulator works
In the real lab, you would slowly turn up the base supply *V_BB* and read
*I_B* off a microammeter. Here, you simply **type in the value of I_B (µA)**
you want to investigate, and the simulator instantly calculates the
*V_BE* that the base supply would need to produce — exactly as if you had
adjusted the supply and taken a meter reading.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================================
# TAB 2 — SIMULATION & DATA LOGGING
# =========================================================================
def simulation_tab():
    st.markdown('<div class="lab-card">', unsafe_allow_html=True)
    st.header("🔬 Simulation & Data Logging")

    with st.expander("⚙️ Power Supply / Circuit Settings", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.session_state.vcc = st.number_input(
                "Collector Supply, V_CC (V)", min_value=3.0, max_value=20.0,
                value=st.session_state.vcc, step=0.5,
            )
        with c2:
            st.session_state.rc_kohm = st.number_input(
                "Collector Resistor, R_C (kΩ)", min_value=0.1, max_value=10.0,
                value=st.session_state.rc_kohm, step=0.1,
            )
        with c3:
            st.session_state.beta = st.number_input(
                "Current gain, β (h_FE)", min_value=20, max_value=400,
                value=int(st.session_state.beta), step=10,
            )

    st.write(
        "Vary the base supply to set a base current, then take a reading. "
        "**V_BE**, **I_C** and **V_CE** will be generated automatically."
    )

    col_in, col_btn = st.columns([2, 1])
    with col_in:
        ib_uA = st.number_input(
            "Set Base Current, I_B (µA)", min_value=0.1, max_value=500.0,
            value=10.0, step=1.0,
        )
    with col_btn:
        st.write("")
        st.write("")
        take_reading = st.button("📥 Take Reading", use_container_width=True)

    if take_reading:
        vbe, ic, vce, region = compute_operating_point(
            ib_uA, st.session_state.vcc, st.session_state.rc_kohm, st.session_state.beta
        )
        st.session_state.readings.append(
            {
                "I_B (µA)": round(ib_uA, 2),
                "V_BE (V)": round(vbe, 4),
                "I_C (mA)": round(ic * 1000, 4),
                "V_CE (V)": round(vce, 4),
                "Region": region,
            }
        )
        st.success(
            f"Reading logged → V_BE = {vbe:.3f} V, I_C = {ic*1000:.3f} mA, "
            f"V_CE = {vce:.3f} V  [{region}]"
        )

    bcol1, bcol2 = st.columns(2)
    with bcol1:
        if st.button("🗑️ Clear All Readings"):
            st.session_state.readings = []
            st.rerun()

    if st.session_state.readings:
        df = pd.DataFrame(st.session_state.readings).sort_values("I_B (µA)")
        st.subheader("📊 Logged Data")
        st.dataframe(df, use_container_width=True, hide_index=True)

        with bcol2:
            st.download_button(
                "⬇️ Download Readings (CSV)",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"{st.session_state.matric}_readings.csv",
                mime="text/csv",
            )

        st.subheader("📈 Characteristic Curves")
        g1, g2, g3 = st.columns(3)

        with g1:
            fig1, ax1 = plt.subplots()
            ax1.plot(df["V_BE (V)"], df["I_B (µA)"], "o-", color="#2b6cb0")
            ax1.set_xlabel("V_BE (V)")
            ax1.set_ylabel("I_B (µA)")
            ax1.set_title("Input Characteristic")
            ax1.grid(alpha=0.3)
            st.pyplot(fig1)

        with g2:
            fig2, ax2 = plt.subplots()
            ax2.plot(df["I_B (µA)"], df["I_C (mA)"], "o-", color="#1b3a57")
            ax2.set_xlabel("I_B (µA)")
            ax2.set_ylabel("I_C (mA)")
            ax2.set_title("Current Transfer Characteristic")
            ax2.grid(alpha=0.3)
            st.pyplot(fig2)

        with g3:
            fig3, ax3 = plt.subplots()
            ax3.plot(df["V_BE (V)"], df["V_CE (V)"], "o-", color="#a1662b")
            ax3.set_xlabel("V_BE (V)")
            ax3.set_ylabel("V_CE (V)")
            ax3.set_title("Voltage Transfer Characteristic")
            ax3.grid(alpha=0.3)
            st.pyplot(fig3)
    else:
        st.info("No readings logged yet. Set I_B above and click **Take Reading**.")

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================================
# TAB 3 — EXERCISES
# =========================================================================
def exercise_tab():
    st.markdown('<div class="lab-card">', unsafe_allow_html=True)
    st.header("📝 Exercises")
    st.write("Answer the following 5 questions based on the practical, then submit.")

    for i, item in enumerate(EXERCISE_QUESTIONS):
        key = f"q{i}"
        st.markdown(f"**{item['q']}**")
        default_index = None
        if key in st.session_state.exercise_answers:
            try:
                default_index = item["options"].index(st.session_state.exercise_answers[key])
            except ValueError:
                default_index = None
        choice = st.radio(
            "Select one:",
            item["options"],
            index=default_index,
            key=f"radio_{key}",
            label_visibility="collapsed",
            disabled=st.session_state.exercise_submitted,
        )
        st.session_state.exercise_answers[key] = choice
        st.markdown("---")

    if not st.session_state.exercise_submitted:
        if st.button("✅ Submit Exercise"):
            answered = [v for v in st.session_state.exercise_answers.values() if v]
            if len(answered) < len(EXERCISE_QUESTIONS):
                st.warning("Please answer all 5 questions before submitting.")
            else:
                score = 0
                for i, item in enumerate(EXERCISE_QUESTIONS):
                    if st.session_state.exercise_answers[f"q{i}"] == item["answer"]:
                        score += 1
                st.session_state.exercise_score = score
                st.session_state.exercise_submitted = True

                row = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "matric_number": st.session_state.matric,
                    "student_name": st.session_state.student_name,
                    "score": score,
                    "total": len(EXERCISE_QUESTIONS),
                }
                for i, item in enumerate(EXERCISE_QUESTIONS):
                    row[f"Q{i+1}_answer"] = st.session_state.exercise_answers[f"q{i}"]
                save_result_row(row)
                st.rerun()
    else:
        score = st.session_state.exercise_score
        total = len(EXERCISE_QUESTIONS)
        st.success(
            f"Exercise submitted! Your score: **{score} / {total}**. "
            "Your performance has been saved and forwarded to your course lecturer."
        )
        for i, item in enumerate(EXERCISE_QUESTIONS):
            given = st.session_state.exercise_answers[f"q{i}"]
            correct = item["answer"]
            if given == correct:
                st.markdown(f"Q{i+1}: <span class='correct-badge'>Correct ✔</span>", unsafe_allow_html=True)
            else:
                st.markdown(
                    f"Q{i+1}: <span class='wrong-badge'>Incorrect ✘</span> "
                    f"— correct answer: *{correct}*",
                    unsafe_allow_html=True,
                )

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================================
# MAIN APP FLOW
# =========================================================================
def main():
    init_state()

    if not st.session_state.logged_in:
        login_page()
        return

    inject_css()

    top_l, top_r = st.columns([4, 1])
    with top_l:
        st.markdown(
            f"""
            <div class="top-banner">
                <h1>🔌 CE Transistor Characteristics — Virtual Lab</h1>
                <span>Logged in as: <b>{st.session_state.student_name or "Student"}</b>
                &nbsp;|&nbsp; Matric No: <b>{st.session_state.matric}</b></span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with top_r:
        st.write("")
        if st.button("🚪 Log Out", use_container_width=True):
            for key in [
                "logged_in", "matric", "student_name", "readings",
                "exercise_answers", "exercise_submitted", "exercise_score",
            ]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

    tab1, tab2, tab3 = st.tabs(
        ["📘 Learn the Basics", "🔬 Simulation & Data Logging", "📝 Exercises"]
    )
    with tab1:
        learn_tab()
    with tab2:
        simulation_tab()
    with tab3:
        exercise_tab()


if __name__ == "__main__":
    main()
