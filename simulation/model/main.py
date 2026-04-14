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

from picounits.extensions.parser import Parser
from picounits import Q, unit_validator, CURRENT, POWER, TIME, NULLSET, RESISTANCE

from simulate import ActiveProblem, PassiveProblem

# Pulls the two parameter
BASE_DIR = Path(__file__).parent
active_parameters = Parser.open(BASE_DIR / "parameters_active.uiv", BASE_DIR / "units.ut")
passive_parameters = Parser.open(BASE_DIR / "parameters_passive.uiv", BASE_DIR / "units.ut")

# normalization factors
i_max = 1 * CURRENT
p_max = 50 * POWER
t_max = 5 * TIME

problem = PassiveProblem(passive_parameters)
print(problem.solve())

# Base values
v_s = passive_parameters.model.battery_voltage
r_p = passive_parameters.resistor.resistance + passive_parameters.capacitor.resistance
c_p = passive_parameters.capacitor.capacitance

r_a = active_parameters.resistor.resistance + active_parameters.capacitor.resistance
c_a = active_parameters.capacitor.capacitance



# @unit_validator(NULLSET)
# def passive_stress(voltage: Q, resistance: Q, capacitance: Q) -> Q:
#     """ Calculates the normalized system stress """
#     current = voltage / (resistance*i_max)
#     power   = voltage ** 2 / (10*resistance * p_max)
#     time    = 5 * resistance * capacitance / t_max

#     return current + power + time

# @unit_validator(NULLSET)
# def active_stress(i_peak: Q, r_power: Q, time: Q) -> Q:
#     """ Calculates the normalized system stress """
#     return i_peak / i_max + r_power / p_max + time / t_max

# # Calculates the passive stresses & active stresses
# resistances = logspace(-1, 4, 5)
# passive_stresses = [
#     passive_stress(v_s, r_val * RESISTANCE, c_p).stripped 
#     for r_val in resistances
# ]

# active_stresses = []
# for r_val in resistances:
#     r_q = r_val * RESISTANCE
#     print(f"Solving active pre-charge problem with {r_q}...")

#     active_parameters.resistor.resistance = r_q
#     problem = ActiveProblem(active_parameters)
#     i, p, t = problem.solve(verbose=False)
#     active_stresses.append(active_stress(i, p, t).stripped)


# # Plotting
# mplot.figure(figsize=(10, 6))

# mplot.plot(resistances, passive_stresses, label='Passive Pre-charge', linewidth=2)
# mplot.plot(
#     resistances, active_stresses, label='Active Pre-charge', linewidth=2, linestyle='--'
# )

# mplot.xscale('log')
# mplot.yscale('log')

# # Add interesting annotations
# mplot.xlabel('Resistance (Ohm)')
# mplot.ylabel('System Stress (Normalized)')
# mplot.title(f'Comparison: Passive vs. Active Stress | $V_s$: {v_s.stripped:.1f}V')
# mplot.legend()
# mplot.grid(True, which="both", ls="-", alpha=0.3)

# mplot.show()
