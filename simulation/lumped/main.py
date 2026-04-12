"""
Filename: main.py

Description:
    Calculates the voltage across the dc linked capacitor
    within the active pre-charger. Uses a fixed PMW frequency 
    to drive the hard-side fet @ 50% duty cycle.
    
    Uses rk2 methods (Ralston's Method) to solve y1 & y2 
    equations modelling:
    -> v_c = v_s - v_r - v_l -> ir + L(di/dt) - v_s
    
    DOCS:
    # Given the current usage of 200uF of dc linked capacitance. 
    # The calculations will consider that a fixed value and optimize
    # L1 & R1 only for simplistically
"""

from pathlib import Path
from matplotlib import pyplot as mplot

from picounits import VOLTAGE, TIME, ENERGY
from picounits.core import unit_validator, Quantity as Q
from picounits.extensions.parser import Parser

BASE_DIR = Path(__file__).parent
parameters = Parser.open(
    BASE_DIR / "parameters.uiv", derived_units= BASE_DIR / "units.ut"
)

@unit_validator(VOLTAGE/TIME ** 2)
def differential_voltage(v_s: Q, ind: Q, res: Q, cap: Q, y1: Q, y2: Q) -> Q:
    """ differential equation for cap voltage """
    return 1 / (ind*cap) * (v_s - res*cap*y2 - y1)


@unit_validator(VOLTAGE/TIME)
def rk_2nd_order_voltage(v_s: Q, ind: Q, res: Q, cap: Q, y1: Q, y2: Q, t_s: Q) -> Q:
    """ Calculates the rate of change of voltage within the system """
    k1_y1 = y2
    k1_y2 = differential_voltage(v_s, ind, res, cap, y1, y2)

    # Calculates derivative at predicted position
    prep_y1, prep_y2 = y1 + 3/4 * k1_y1 * t_s, y2 + 3/4 * k1_y2 * t_s
    k2_y2 = differential_voltage(v_s, ind, res, cap, prep_y1, prep_y2)

    return (1/3 * k1_y2 + 2/3 * k2_y2) * t_s

# Extraction of parameters from configuration file
time_domain, supply= parameters.model.time_domain, parameters.model.voltage

r1 = parameters.components.r1
l1 = parameters.components.l1
c1 = parameters.components.c1
m1_area = parameters.components.m1_area
m1_rds = parameters.components.m1_rds

# Uses 1/10 of time constant as step size -> ensures numerical stability
step = l1 / (10 * r1)
msg_step = (5 * r1*c1) / (step * parameters.display.num_messages)

# Loop variables
electrical_energy = 0.0 * ENERGY
fet_temperature = parameters.model.ambient
voltages = [] * VOLTAGE

time, v, dv_dt = 0.0 * TIME, 0.0 * VOLTAGE, 0.0 * (VOLTAGE / TIME)
while time < time_domain:
    # Mimics a comparator -> instantaneous current regulation
    current = c1 * dv_dt
    current_limit = 1/2 * supply / r1

    voltage = 0.0 * VOLTAGE
    if current < current_limit:
        voltage = supply

    electrical_energy += current*v*step

    # Calculates the heating within the FET
    fet_power = current ** 2 * m1_rds
    heating = (fet_power * step) / parameters.components.m1_thermal_mass
    cooling = (
        (
            (fet_temperature - parameters.model.ambient)
            * parameters.model.case_convection
            * m1_area * step
        ) / parameters.components.m1_thermal_mass
    )

    fet_temperature += (heating - cooling)
    voltages.append(v)

    # Calculates the rate of voltage change
    dv = rk_2nd_order_voltage(voltage, l1, r1, c1, v, dv_dt, step)

    # Updates state for next time
    v, dv_dt = v + (dv_dt * step), dv_dt + dv
    time += step

    # prints current state every x steps
    if round(len(voltages) % msg_step.stripped, 3) == 0:
        print(f"Time: {time:.3f}, Cap voltage: {v:.3f}, energy: {electrical_energy:.3f}")
        print(f"FET current: {current:.3f}, FET temperature: {fet_temperature:.3f}")

    # Finish the simulation early if wind up is successful
    if v > (0.99) * supply:
        time += time_domain

# Graphs the voltage curve in matplotlib
v_out = voltages.stripped
time = [i * step.stripped for i in range(0, len(v_out))]

mplot.plot(time, v_out)
mplot.title('DC Capacitor Voltage vs Time')
mplot.xlabel('Time (s)')
mplot.ylabel('Voltage (V)')
mplot.grid(True)

mplot.show()
