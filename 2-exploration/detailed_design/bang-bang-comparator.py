"""
Filename: bang-bang-comparator.py

Description:
    Calculations for the bang-bang comparator hysteresis to
    ensure that the output voltage is within the target
    range.
"""
from pathlib import Path
from picounits.configuration.config import get_derived_units

from picounits import RESISTANCE, VOLTAGE, CURRENT, KILO, MILLI

# Imports derived units
BASE_DIR = Path(__file__).parent
derived = get_derived_units(BASE_DIR / "units.ut")

# System variables
v_main = 600 * VOLTAGE
v_iso = 5 * VOLTAGE
r_shunt = 5 * RESISTANCE

i_peak = 500 * MILLI * CURRENT
i_min = 200 * MILLI * CURRENT

# Hysteresis triggers (high, low)
v_h = i_peak * r_shunt
v_l = i_min * r_shunt

print(f"Hysteresis triggers: {v_h:.3f}, {v_l:.3f}")

# resistor sizing
r1 = 240 * KILO * RESISTANCE        # Arbitrary sizing -> decrease space

protection = v_main / (10*MILLI*CURRENT)
print(f"Protection Resistor @ {10*MILLI*CURRENT}: {protection:.3f}")

standard_resistor_series = [
    1, 10, 100, 1.1, 11, 110, 1.2, 12, 120, 1.3, 13, 130, 1.5, 15, 150, 
    1.6, 16, 160, 1.8, 18, 180, 2, 20, 200, 2.2, 22, 220, 2.4, 24, 240, 
    2.7, 27, 270, 3, 30, 300, 3.3, 33, 330, 3.6, 36, 360, 3.9, 39, 390, 
    4.3, 43, 430, 4.7, 47, 470, 5.1, 51, 510, 5.6, 56, 560, 6.2, 62, 620, 
    6.8, 68, 680, 7.5, 75, 750, 8.2, 82, 820, 9.1, 91, 910, 1000, 10000, 
    100000, 1100, 11000, 110000, 1200, 12000, 120000, 1300, 13000, 130000, 
    1500, 15000, 150000, 1600, 16000, 160000, 1800, 18000, 180000, 2000, 
    20000, 200000, 2200, 22000, 220000, 2400, 24000, 240000, 2700, 27000, 
    270000, 3000, 30000, 300000, 3300, 33000, 330000, 3600, 36000, 360000, 
    3900, 39000, 390000, 4300, 43000, 430000, 4700, 47000, 470000, 5100, 
    51000, 510000, 5600, 56000, 560000, 6200, 62000, 620000, 6800, 68000, 
    680000, 7500, 75000, 750000, 8200, 82000, 820000, 9100, 91000, 910000, 
    1000000, 3000000, 9100000, 1100000, 3300000, 10000000, 1200000, 3600000, 
    12000000, 1300000, 3900000, 13000000, 1500000, 4300000, 15000000, 1600000, 
    5100000, 16000000, 1800000, 5600000, 18000000, 2000000, 6200000, 20000000, 
    2200000, 6800000, 22000000, 2400000, 7500000, 2700000, 8200000, 0.5, 0.22
] * RESISTANCE

for i in standard_resistor_series:
    break
    r1 = i
    r2 = (v_l * r1) / (v_h - v_l)
    r3 = (r1 * v_l) / (v_iso - v_h)

    try:
        # Calculates the "real" activation
        vh = r3 * v_iso * (r1 + r2) / (r1 * r2 + r1 * r3 + r2 * r3)
        vl = vh - r3 * (v_iso - vh) / r2

        print(f"Comparator {r1:.3f}, {r2:.3f}, {r3:.3f}| v_l: {vl:.3f}, v_h: {vh:.3f}")
    except Exception as err:
        continue

r1 = 15.00 * KILO * RESISTANCE
r2 = 10 * KILO * RESISTANCE
r3 = 6 * KILO * RESISTANCE

v_h = r3 * v_iso * (r1 + r2) / (r1 * r2 + r1 * r3 + r2 * r3)
v_l = v_h - r3 * (v_iso - v_h) / r2

print(f"Real Hysteresis triggers @ {r1:.3f}, {r2:.3f}, {r3:.3f}: {v_h:.3f}, {v_l:.3f}")  