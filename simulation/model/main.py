"""
Filename: main.py

Descriptions:
    Calculates the voltage across the dc linked capacitor
    within the active pre-charger. Uses a comparator as feedback
    to limit current across the LRC abstract element.
    
    Reference:
    - open parameters_active.uiv for simulation details
    - open parameters_passive.uiv for simulation details
"""


from pathlib import Path
from numpy import logspace
from matplotlib import pyplot as mplot
# from matplotlib import cm

from picounits.extensions.parser import Parser
from picounits import Q, unit_validator, CURRENT, POWER, TIME, NULLSET, RESISTANCE

# from simulate import ActiveProblem

# Pulls the two parameter
BASE_DIR = Path(__file__).parent
active_parameters = Parser.open(BASE_DIR / "parameters_active.uiv", BASE_DIR / "units.ut")
passive_parameters = Parser.open(BASE_DIR / "parameters_passive.uiv", BASE_DIR / "units.ut")

# normalization factors
i_max = 1 * CURRENT
p_max = 50 * POWER
t_max = 5 * TIME

# Base values
v_s = active_parameters.model.battery_voltage
r = active_parameters.resistor.resistance + active_parameters.capacitor.resistance
c = active_parameters.capacitor.capacitance

@unit_validator(NULLSET)
def passive_stress(voltage: Q, resistance: Q, capacitance: Q) -> Q:
    """ Calculates the normalized system stress """
    current = voltage / (resistance*i_max)
    power   = voltage ** 2 / (10*resistance * p_max)
    time    = 5 * resistance * capacitance / t_max

    return current + power + time

resistances = logspace(-1, 4, 500)
stresses = [passive_stress(v_s, r_val * RESISTANCE, c).stripped for r_val in resistances]

min_stress = min(stresses)
best_r = resistances[stresses.index(min_stress)]
print(f"The optimal resistance is {best_r:.2f} Ohms with a stress of {min_stress:.2f}")


# Plotting
mplot.figure(figsize=(10, 6))
mplot.plot(resistances, stresses)
mplot.yscale('log')
mplot.xlabel('Resistance (Ohm)')
mplot.ylabel('System Stress (Normalized)')
mplot.title(f'Resistor Value vs. System Stress | c_dc: {c:.3f} v_s: {v_s:.3f}')
mplot.grid(True, which="both", ls="-")
mplot.show()

# problem = ActiveProblem(active_parameters)
# time, voltage, current = problem.solve(False)
