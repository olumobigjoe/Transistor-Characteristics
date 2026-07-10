# CE Transistor Characteristics — Virtual Lab

An interactive Streamlit simulator for physics/electronics students to
determine the **Input**, **Current Transfer**, and **Voltage Transfer**
characteristics of a Common-Emitter (CE) connected NPN transistor.

## How to run

1. Install Python 3.9+ if you don't already have it.
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the app:
   ```bash
   streamlit run app.py
   ```
4. Your browser will open automatically at `http://localhost:8501`.

## What's inside

- **Login** — students log in with their matric number (format-checked only;
  no roster is required). No password is needed.
- **📘 Learn the Basics** — a short explainer on the CE configuration, the
  components involved, a circuit schematic, and what each characteristic
  curve means.
- **🔬 Simulation & Data Logging** — students set a base current *I_B* (µA);
  the app automatically calculates the corresponding *V_BE*, *I_C* and
  *V_CE* using a standard diode/Ebers–Moll-style transistor model, logs
  each reading to a table, and live-plots all three characteristic curves.
  V_CC, R_C and β (current gain) are adjustable under "Power Supply /
  Circuit Settings" to represent varying the lab power supply.
- **📝 Exercises** — 5 multiple-choice questions based on the practical.
  On submission, the score and answers are saved automatically to
  `lab_data/student_results.csv` (one row per submission, with matric
  number, name, timestamp, score, and answers) — this file is what you
  hand/forward to the course lecturer.
- **Log Out** button clears the session and returns to the login screen.

## Notes for the lecturer

- All student submissions accumulate in `lab_data/student_results.csv`
  in the same folder the app is run from. Open it in Excel/Sheets to
  review class performance.
- The transistor model uses: thermal voltage V_T ≈ 0.02585 V, saturation
  current I_S = 1e-14 A, default β = 100, and V_CE(sat) = 0.2 V. These
  can be tuned in `app.py` (top constants) if you want to match a
  specific transistor datasheet.
- Because there's no roster check, any correctly-formatted matric number
  is accepted. If you'd like it validated against your actual class list
  instead (e.g. an uploaded CSV of registered students), that's a
  straightforward follow-up change — just ask.

## Customizing

- Colors/theme: edit the `inject_css()` function in `app.py`.
- Exercise questions: edit the `EXERCISE_QUESTIONS` list in `app.py`.
- Circuit values: edit `VT`, `IS`, `BETA_DEFAULT`, `VCE_SAT` constants.
