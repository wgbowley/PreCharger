"""
Filename: simulate.py

Descriptions:
    Solve dc linked capacitor voltage while modelling a 
    comparator to ensure current is below current limit. 
"""

from math import exp
from builtins import float as f

from picounits import Q, strip_quantity as qstrip
from picounits.extensions.loader import DynamicLoader

from picounits import (
    TEMPERATURE, VOLTAGE, CURRENT, CONVECTION_COEFFICIENT, CAPACITANCE,
    INDUCTANCE, LENGTH, TIME, ENERGY, POWER
)


def differential_slew_state(v_s: f, ind: f, res: f, cap: f, v: f, dv_dt: f) -> f:
    """ calculates the rate of change of the transfer function """
    upper = v_s - res * cap * dv_dt - v
    return upper / (ind * cap)

def differential_voltage(v_s: f, v_c: f, rc: f) -> f:
    """ Calculates the rate of change of the voltage within the cap"""
    return (v_s - v_c) / rc

def rk_2nd_order_solve(v_s: f, ind: f, res: f, cap: f, v: f, dv_dt: f, t_s: f) -> f:
    """ Uses ralston method to solve dv/dt differential equation """
    k1_v = v
    k1_dv_dt = differential_slew_state(v_s, ind, res, cap, v, dv_dt)

    # Calculates derivative at predicted next position
    pred_v = v + 3/4 * k1_v * t_s
    pred_dv_dt = dv_dt + 3/4 * k1_dv_dt * t_s

    k2_dv_dt = differential_slew_state(v_s, ind, res, cap, pred_v, pred_dv_dt)
    return (1/3 * k1_dv_dt + 2/3 * k2_dv_dt) * t_s


class ActiveProblem:
    """ Defines the problem and solves it """
    def __init__(self, parameters: DynamicLoader) -> None:
        """ Initializes the problem & extracts / validates / strips qualities """
        self.extract_and_strip(parameters)

        # derived values
        self.total_resistance = self.R_resistance + self.C_resistance + self.L_resistance
        self.RC_constant = self.C_capacitance * self.total_resistance

        self.upper_threshold = self.current_limit - self.Comp_h_curr
        self.lower_threshold = self.upper_threshold - self.Comp_h_curr

        self.msg_step = int((5 * self.RC_constant) / (self.step * self.msg_count))

    def solve(self, verbose: bool = True) -> list[Q,Q,Q]:
        """ Solves the problem defined during Initialization """
        voltage_series = []
        current_series = []
        time_series = []
        fet_power = []
        r_power = []

        fet_temperature = self.ambient_temperature

        comp_out = target = time = v = msg = dv_dt = C_energy = 0
        while time < self.domain:
            C_current = self.C_capacitance * dv_dt

            # Analytical model of a current limiting comparator
            if C_current > self.upper_threshold:
                target = 0
            elif C_current < self.lower_threshold:
                target = 1

            alpha = 1 - exp(-self.step / self.Comp_t_cons)
            comp_out += (target - comp_out) * alpha
            comp_out = max(0.0, min(1.0, comp_out))

            # Calculates source voltage & electrical energy
            S_voltage = self.battery_voltage * comp_out
            C_energy += C_current * v * self.step

            # Calculates the heating within the FET
            heating = C_current ** 2 * self.F_rds

            difference = fet_temperature - self.ambient_temperature
            cooling = difference * self.F_area * self.convection

            fet_temperature += (heating - cooling) * self.step / self.F_Tmass

            # Calculates the rate of change of voltage
            dv = rk_2nd_order_solve(
                S_voltage, self.L_inductance, self.total_resistance,
                self.C_capacitance, v, dv_dt, self.step
            )

            # Saves current & voltage state
            time_series.append(time)
            voltage_series.append(v)
            current_series.append(C_current)
            fet_power.append(heating)
            r_power.append(C_current**2 * self.R_resistance)

            # Updates states for next step
            v, dv_dt = v + dv_dt * self.step, dv_dt + dv
            time += self.step
            msg += 1

            # Prints out current state variables
            if msg > self.msg_step and verbose:
                print(
                    f"t: {time*TIME:.3f}"
                    f", C_I: {C_current*CURRENT:.3f}"
                    f", C_v: {v*VOLTAGE:.3f}"
                    f", C_e: {C_energy*ENERGY:.3f}"
                    f", F_p: {heating*POWER:.3f}"
                    f", F_t: {fet_temperature*TEMPERATURE:.3f}"
                )
                msg = 0

            if v > 0.99 * self.battery_voltage:
                break

        if verbose:
            average_power = sum(fet_power) / len(fet_power)
            asymptotic_temp = self.F_Trate * average_power + self.ambient_temperature
            frequency_max = self.battery_voltage / (2 * self.L_inductance * self.current_limit)
            print(
                f"====  Model Parameters ====\n"
                f"F_avp: {average_power*POWER:.3f}",
                f", F_t: {fet_temperature*TEMPERATURE:.3f}"
                f", F_at: {asymptotic_temp*TEMPERATURE:.3f}"
                f", di_dt: {self.battery_voltage/self.L_inductance*(VOLTAGE/INDUCTANCE):.3f}"
                f", f_max: {frequency_max*(1/TIME):.3f}"
                f"\n==========================="
            )

        time = max(time_series)
        current = max(current_series)
        avg_r_power = sum(r_power) / len(r_power)
        return current * CURRENT, avg_r_power * POWER, time * TIME

    def extract_and_strip(self, parameters: DynamicLoader) -> None:
        """ Extracts and strips units from configuration file while validating """
        self.step = qstrip(parameters.numerics.time_step, TIME)
        self.domain = qstrip(parameters.numerics.time_domain, TIME)
        self.msg_count = parameters.numerics.msg_display.stripped

        self.ambient_temperature = qstrip(parameters.model.ambient_temperature, TEMPERATURE)
        self.battery_voltage = qstrip(parameters.model.battery_voltage, VOLTAGE)
        self.current_limit = qstrip(parameters.model.current_limit, CURRENT)
        self.convection = qstrip(parameters.model.convection, CONVECTION_COEFFICIENT)

        self.R_resistance = qstrip(parameters.resistor.resistance, VOLTAGE / CURRENT)

        self.L_resistance = qstrip(parameters.inductor.resistance, VOLTAGE / CURRENT)
        self.L_inductance = qstrip(parameters.inductor.inductance, INDUCTANCE)

        self.C_resistance = qstrip(parameters.capacitor.resistance, VOLTAGE / CURRENT)
        self.C_capacitance = qstrip(parameters.capacitor.capacitance, CAPACITANCE)

        self.F_area = qstrip(parameters.fet.area, LENGTH ** 2)
        self.F_rds = qstrip(parameters.fet.rds, VOLTAGE / CURRENT)
        self.F_Tmass = qstrip(parameters.fet.thermal_mass, ENERGY / TEMPERATURE)
        self.F_Trate = qstrip(parameters.fet.thermal_rate, TEMPERATURE / POWER)
        self.Comp_t_cons = qstrip(parameters.comparator.time_constant, TIME)
        self.Comp_h_curr = qstrip(parameters.comparator.hyst_current, CURRENT)


class PassiveProblem:
    """ Defines the problem and solves it"""
    def __init__(self, parameters: DynamicLoader) -> None:
        """ Initializes the problem & extracts / validates / strip qualities """
        self.extract_and_strip(parameters)

        self.total_res = self.R_resistance + self.C_resistance
        self.rc_constant = self.total_res * self.C_capacitance

        self.msg_step = int((5 * self.rc_constant) / (self.step * self.msg_count))

    def solve(self, verbose: bool = True) -> tuple[Q,Q,Q]:
        """ Solves the problem defined during the initialization """
        time_series = []
        voltage_series = []
        current_series = []
        r_power_series = []

        time = v = dv_dt = C_energy = msg = 0.0
        while time < self.domain:
            # Calculates capacitor voltage & energy delta
            C_current = self.C_capacitance * dv_dt
            C_energy += C_current * v * self.step

            # Calculates the dv/dt of the system
            dv_dt = differential_voltage(self.battery_voltage, v, self.rc_constant)
            v += dv_dt * self.step
            time += self.step
            msg += 1

            # Saves current & voltage state
            time_series.append(time)
            voltage_series.append(v)
            current_series.append(C_current)
            r_power_series.append(C_current ** 2 * self.R_resistance)

            if msg > self.msg_step and verbose:
                print(
                    f"t: {time*TIME:.3f}"
                    f", C_v: {v:.3f}"
                    f", C_I: {C_current*CURRENT:.3f}"
                    f", C_E: {C_energy*ENERGY:.3f}"
                )
                msg = 0

            if v > 0.99 * self.battery_voltage:
                break

        time = max(time_series)
        current = max(current_series)
        avg_r_power = sum(r_power_series) / len(r_power_series)
        return current * CURRENT, avg_r_power * POWER, time * TIME

    def extract_and_strip(self, parameters: DynamicLoader) -> None:
        """ Extracts and strips units from configuration file while validating """
        self.step = qstrip(parameters.numerics.time_step, TIME)
        self.domain = qstrip(parameters.numerics.time_domain, TIME)
        self.msg_count = parameters.numerics.msg_display.stripped

        self.battery_voltage = qstrip(parameters.model.battery_voltage, VOLTAGE)

        self.R_resistance = qstrip(parameters.resistor.resistance, VOLTAGE / CURRENT)

        self.C_resistance = qstrip(parameters.capacitor.resistance, VOLTAGE / CURRENT)
        self.C_capacitance = qstrip(parameters.capacitor.capacitance, CAPACITANCE)
