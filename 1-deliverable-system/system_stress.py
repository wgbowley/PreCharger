"""
Filename: System_stress.py

Description:
    This program performs these key validation checks:
    A: 
    Under continuous loading the pre-charger resistor 
    will not exclude operational temperature.
    
    B: Under continuous loading the pre-charger mechanical 
    relay will not exclude operational temperature.
    
    NOTE: pip install picounits
    NOTE: This is WORST case calculations were the capacitor has shorted across
    and the resistors are passing their ohmic value.
    
    NOTE: Resistor is PWR263S-35 35W TO-263. Relay is KT24-1A-40L-SMD.
    
    ASSUMPTION:
    An abstract resistor made of a few series resistors. Is reasonable as an analytical method
"""

from pathlib import Path
from picounits.configuration.config import get_derived_units

from picounits import POWER, TEMPERATURE, TIME, CAPACITANCE, VOLTAGE, RESISTANCE, MICRO, MILLI

# Fetches user defined notation
_ = get_derived_units(Path(__file__).parent / "units.ut")

# SYSTEM VARIABLES
ACCUMULATOR_VOLTAGE = 600 * VOLTAGE
NUM_RESISTORS = 6

RAISE_TIME = 4.5 * TIME
LINKED_CAPACITANCE = 240 * MICRO * CAPACITANCE
RELAY_RES = 200 * MILLI * RESISTANCE                        # (WORST CASE)

RESISTOR_MAX_POWER = 20 * POWER

ATMOSPHERIC = 329.85 * TEMPERATURE                          # Hottest day on recorded
TEMPERATURE_LIMIT = 428.15 * TEMPERATURE


# Calculations
pre_charger_resistor_res = RAISE_TIME / (3 * LINKED_CAPACITANCE)
energy_dissipated = 0.5 * LINKED_CAPACITANCE * (ACCUMULATOR_VOLTAGE ** 2)

total_resistance = pre_charger_resistor_res + RELAY_RES
total_current = ACCUMULATOR_VOLTAGE / total_resistance

relay_losses = total_current ** 2 * RELAY_RES
resistor_losses = total_current ** 2 * (pre_charger_resistor_res / NUM_RESISTORS)

# Solutions (Resistor Size, Power losses, Heating)
print("=== Pre-charger Resistor Sizing (Fixed Value) ===")
print(f"{pre_charger_resistor_res/NUM_RESISTORS:.3f}, x{NUM_RESISTORS} in series")
print(f"Energy dissipated in resistors: {energy_dissipated:.3f}")

print("===  Worst-Case Continuous Fault (Cap Shorted) ===")
print(f"Resistor power={resistor_losses:.3f}")
print(f"Resistor power_fraction: {resistor_losses/RESISTOR_MAX_POWER:.3f}")