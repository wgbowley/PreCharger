"""
Filename: main.py

Descriptions:
    Calculates the voltage across the dc linked capacitor
    within the active pre-charger. Uses a comparator as feedback
    to limit current across the LRC abstract element.
    
    Reference: open parameters.uiv for simulation details.
    
    DOCS:
    
"""


from pathlib import Path
from picounits.extensions.parser import Parser

from simulate import ActiveProblem

BASE_DIR = Path(__file__).parent
active_parameters = Parser.open(BASE_DIR / "parameters_active.uiv", BASE_DIR / "units.ut")

problem = ActiveProblem(active_parameters)
time, voltage, current = problem.solve()
