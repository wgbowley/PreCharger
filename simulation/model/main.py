"""
Filename: main.py

Descriptions:
    Calculates the voltage across the dc linked capacitor
    within the active pre-charger. Uses a comparator as feedback
    to limit current across the LRC abstract element.
    
    Reference:
    - open parameters_active.uiv for simulation details
    - open parameters_passive.uiv for simulation details
    
    DOCS:
    # May take 1-5 minutes to solve due to the 50nS of the active pre-charger circuit. 
    # This is due to comparator and the di/dt being quite massive. So to control it. The
    # loop has to be very fast.
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

problem = ActiveProblem(active_parameters)
print(problem.solve())

problem = PassiveProblem(passive_parameters)
print(problem.solve())

# normalization factors
i_max = 1 * CURRENT
p_max = 50 * POWER
t_max = 5 * TIME

# Base values
v_s = passive_parameters.model.battery_voltage
r_p = passive_parameters.resistor.resistance + passive_parameters.capacitor.resistance
c_p = passive_parameters.capacitor.capacitance

r_a = active_parameters.resistor.resistance + active_parameters.capacitor.resistance
c_a = active_parameters.capacitor.capacitance


@unit_validator(NULLSET)
def passive_stress(voltage: Q, resistance: Q, capacitance: Q) -> Q:
    """ Calculates the normalized system stress """
    current = voltage / (resistance*i_max)
    power   = voltage ** 2 / (10*resistance * p_max)
    time    = 5 * resistance * capacitance / t_max

    return current + power + time

@unit_validator(NULLSET)
def active_stress(i_peak: Q, r_power: Q, time: Q) -> Q:
    """ Calculates the normalized system stress """
    return i_peak / i_max + r_power / p_max + time / t_max

# Calculates the passive stresses & active stresses
resistances = logspace(-1, 4, 50)
passive_stresses = [
    passive_stress(v_s, r_val * RESISTANCE, c_p).stripped
    for r_val in resistances
]

index = 0
length = len(resistances)
active_stresses = []
for r_val in resistances:
    r_q = r_val * RESISTANCE

    active_parameters.resistor.resistance = r_q
    problem = ActiveProblem(active_parameters)
    i, p, t = problem.solve(verbose=False)
    active_stresses.append(active_stress(i, p, t).stripped)

    index += 1
    print(f"{index}:{length} | Solved active problem @ {r_q:.3f} | {i:.3f}, {p:.3f}, {t:.3f}")


# Plotting
mplot.figure(figsize=(10, 6))

mplot.plot(resistances, passive_stresses, label='Passive', linewidth=2)
mplot.plot(
    resistances, active_stresses, label='Active', linewidth=2, linestyle='--'
)

mplot.xscale('log')
mplot.yscale('log')

# Add interesting annotations
mplot.xlabel('Resistance (Ohm)')
mplot.ylabel('System Stress (Normalized)')
mplot.title(f'Comparison: Passive vs. Active Stress | $V_s$: {v_s.stripped:.1f}V')
mplot.legend()
mplot.grid(True, which="both", ls="-", alpha=0.3)

mplot.show()
