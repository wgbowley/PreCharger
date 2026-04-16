"""
Filename: inductor-selection.py

Description:
    Calculations for the inductor selection in the pre-charger LRC circuit
    via using the TLV701 Comparators.


"""

from math import pi

from pathlib import Path
from picounits.configuration.config import get_derived_units
from picounits.core import unit_validator, quantities as Q

from picounits import (
    INDUCTANCE, RESISTANCE, VOLTAGE, CURRENT, CAPACITANCE, 
    TIME, CHARGE, KILO, MILLI, MICRO, NANO, FREQUENCY
)

# Imports derived units
BASE_DIR = Path(__file__).parent
derived = get_derived_units(BASE_DIR / "units.ut")

# System variables
v_main = 600 * VOLTAGE
i_limit = 200 * MILLI * CURRENT

i_control = i_limit / (1 * MICRO * TIME)

# limiting frequency by supply current 
supply_max_current = 20 * MILLI * CURRENT
gate_charge = 32 * NANO * CHARGE
charge = 1.2 * gate_charge / supply_max_current # 20% extra -> 40% extra just to ensure headroom

limit_freq = 1 / (2 * charge)       # Assumes discharge and charge is similar.

# Uses average ('typical') values for tlv7002 response time
tlv702_res = [260, 310] * TIME
tlv702_res = (tlv702_res[0] + tlv702_res[1])/2

# In-series resistor & capacitor
r1 = 5 * RESISTANCE
c1 = 240 * MILLI * CAPACITANCE

@unit_validator(INDUCTANCE)
def calculated_inductance(v:Q, di_dt: Q) -> Q:
    """ Calculates the inductor size based on voltage & di/dt """
    return v / di_dt

@unit_validator(FREQUENCY)
def max_frequency(v: Q, l: Q, di_peak: Q) -> Q:
    """calculates max frequency | di_peak = inductor peak-to-peak current (ripple) """
    return v / (4 * l * di_peak)

l1 = calculated_inductance(v_main, i_control)
m_f = max_frequency(v_main, l1, i_limit)

if m_f > limit_freq:
    print(f"This configuration is too fast for the TPS: {m_f}: {limit_freq}")

print(f"{i_limit:.3f} | {l1:.3f} : {m_f:.3f} | {1/(2*pi*(l1 * c1)**0.5):.3f}")
