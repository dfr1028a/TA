import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# --- 1. SETUP ---
st.set_page_config(page_title="Frisch's Analyzer - OG APP", layout="wide")
st.title("⛳ Frisch's Torque Influence Analyzer")

# --- 2. INPUT VARIABLES ---
with st.sidebar:
    st.header("Input Variables")
    speed = st.number_input("Speed (mph)", 1.0, 10.0, 3.5, 0.1)
    weight = st.number_input("Head Weight (g)", 300.0, 500.0, 360.0, 1.0)
    static_offset = st.number_input("Lever arm (shaft axis to CG offset)", 0.0, 2.5, 0.75, 0.01)
    lie_angle = st.number_input("Lie Angle (deg)", 60.0, 79.0, 70.0, 0.5)
    lean_deg = st.number_input("Shaft Lean (deg)", -2.0, 2.0, 0.0, 1.0)
    grip_dia = st.number_input("Grip Dia (in)", 0.800, 1.670, 0.900, 0.005)
    # Updated label: Grip Tension (PSI)
    psi_val = st.number_input("Grip Tension (PSI)", 1.0, 10.0, 3.0, 0.1)
    
    st.divider()
    grip_type = st.radio("Grip Material (Dry)", ["Standard Rubber", "Polyurethane"])
    f_mu = 1.25 if grip_type == "Polyurethane" else 1.0

# --- 3. PHYSICS ENGINE ---
lean_rad = (lean_deg * 3.14159) / 180.0
eff_offset = static_offset + (np.sin(lean_rad) * 1.5)

lie_rad = np.radians(90.0 - lie_angle)
lie_factor = np.sin(lie_rad)
base_slope = 0.086 * (weight / 360.0) * (speed / 3.5)
slope_val = base_slope * lie_factor

leverage = (grip_dia / 0.900) * (psi_val / 3.0) * f_mu
t1, t2, t3 = (0.04 * leverage), (0.10 * leverage), (0.20 * leverage)

point_torque = slope_val * eff_offset
radius_m = (grip_dia / 2.0) / 39.37
cap_pct = (point_torque / t3) * 100.0 if t3 > 0 else 0

# --- 4. MAIN INTERFACE ---
col_chart, col_defs = st.columns([3, 1])

with col_chart:
    fig, ax1 = plt.subplots(figsize=(10, 6.5))
    ax2 = ax1.twinx()

    ax1.set_ylim(0, 0.24)
    ax1.set_yticks(np.arange(0, 0.26, 0.02))
    ax1.set_ylabel("Peak Torque (Nm)", fontweight='bold')

    ax1.set_xlim(0, 2.5)
    ax1.set_xticks(np.arange(0, 2.75, 0.25))
    ax1.set_xlabel("Lever arm (shaft axis to CG offset)", fontweight='bold')
    
    y2_ticks = np.arange(0, 130, 10)
    ax2.set_ylim(0, 120)
    ax2.set_yticks(y2_ticks)
    ax2.set_yticklabels([str(p) + "%" for p in y2_ticks])
    ax2.set_ylabel("Grip Capacity %", color='#c0392b', fontweight='bold')

    # Color Zones
    ax1.axhspan(0.0, t1, color='#f1c40f', alpha=0.3)
    ax1.axhspan(t1, t2, color='#3498db', alpha=0.3)
    ax1.axhspan(t2, t3, color='#2ecc71', alpha=0.3)
    ax1.axhspan(t3, 0.24, color='#e74c3c', alpha=0.3)

    x_line = np.linspace(0.0, 2.5, 100)
    ax1.plot(x_line, slope_val * x_line, color='#2c3e50', linewidth=2, linestyle='--')
    ax1.scatter([eff_offset], [point_torque], color='black', s=200, edgecolor='white', zorder=10)
    
    ax1.grid(True, linestyle=':', alpha=0.5)
    st.pyplot(fig)

with col_defs:
    st.subheader("Zone Definitions")
    st.error("**RED: BREAKAWAY**\nTorque exceeds grip stability.")
    st.success("**GREEN: INFLUENTIAL**\nManual effort required.")
    st.info("**BLUE: NOTICEABLE**\nHuman JND threshold reached.")
    st.warning("**YELLOW: UNNOTICEABLE**\nTorque below sensory threshold.")

    st.divider()
    force_val = int(point_torque / radius_m) if radius_m > 0 else 0
    st.metric("Grip Capacity", f"{cap_pct:.1f}%")
    st.metric("Applied Force", f"{force_val} N")
    st.metric("Live Torque", f"{point_torque:.3f} Nm")