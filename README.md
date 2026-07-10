# Transistor Characteristics Simulator

An interactive physics laboratory simulation designed for electronics students to explore the characteristics of a common-emitter connected NPN transistor. This tool allows students to log data in a virtual environment and complete post-lab exercises.

## 🚀 Overview
This application is built using **Python** and **Streamlit**. It provides a controlled, virtual lab experience where students can manipulate the base-emitter voltage ($V_{BE}$), log current values, and visualize the characteristic curves (input, current transfer, and voltage transfer).

## 🛠 Features
- **Student Authentication:** Secure access control using student matriculation numbers.
- **Interactive Simulation:**
    - Real-time adjustment of $V_{BE}$ via sliders.
    - Automated calculation of Base Current ($I_B$) using the Shockley diode equation.
    - Live data logging and graphical visualization of transistor behavior.
- **Learning Module:**
    - Dedicated tab for theoretical basics and circuit diagrams.
    - Built-in post-lab quiz (5 questions).
- **Automated Reporting:**
    - Performance tracking and automated data forwarding to the course lecturer via email.
- **User Interface:** A custom, visually appealing aesthetic with a blue-to-cream gradient theme.

## 📦 Tech Stack
- **Frontend/Backend:** Streamlit
- **Data Manipulation:** Pandas, NumPy
- **Communication:** `smtplib` (for automated reporting)
- **Deployment:** Streamlit Cloud or local hosting

## 🔧 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/olumobigjoee/transistor-simulator.git](https://github.com/olumobigjoe/transistor-simulator.git)
   cd transistor-simulator
