"""
Filename: calculations.py

Description:
    Calculations for the active pre-charger circuit
    specifically the L1, R1, C1 which makes up the
    RLC circuit that the FET connects +bat to.
    
    DOCS:
    # Given the current usage of 200uF of dc linked capacitance. 
    # The calculations will consider that a fixed value and optimize
    # L1 & R1 only for simplistically
"""

from pathlib import Path
from picounits import VOLTAGE, CAPACITANCE, INDUCTANCE, TIME, MILLI, MICRO
from picounits.configuration.config import get_derived_units

# Imports derived units
BASE_DIR = Path(__file__).parent
derived = get_derived_units(BASE_DIR / "units.ut")

# System variables
pack_voltage = 600 * VOLTAGE
charge_time = 200 * MILLI * TIME

C1 = 200 * MICRO * CAPACITANCE
R1 = charge_time / (5 * C1)

# Arbitrary inductance size
L1 = 100 * MICRO * INDUCTANCE

# Power
power_average = C1 * pack_voltage ** 2 / (2 * charge_time)
power_peak = pack_voltage ** 2 / R1

# Current
i_resistor = pack_voltage / R1
i_cap = C1 * (pack_voltage) / (charge_time)
di_dt = pack_voltage / L1

print(f"r: {R1}, p_avg: {power_average}, p_peak: {power_peak}")
print(f"I_cap: {i_cap}, di_dt (slew_rate): {di_dt:.2f}, max_I: {i_resistor}")

print(f"Charging: {R1 * C1:.3f}, filtering/switching: {L1/R1}")
print(f"stored_energy: {1/2*C1*pack_voltage**2:.3f}")


# FET selection
print(f"max_voltage: {pack_voltage*1.5}, max_current: {2*i_resistor}")
