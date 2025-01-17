from collections import deque
from statistics import mean

from custom_components.sat.const import *


class HeatingCurve:
    def __init__(self, heating_system: str, coefficient: float):
        """
        :param heating_system: The type of heating system, either "underfloor" or "radiator"
        :param coefficient: The coefficient used to adjust the heating curve
        """
        self._coefficient = coefficient
        self._heating_system = heating_system
        self.reset()

    def reset(self):
        self._optimal_coefficient = None
        self._last_heating_curve_value = None
        self._optimal_coefficients = deque(maxlen=5)

    def update(self, target_temperature: float, outside_temperature: float) -> None:
        """Calculate the heating curve based on the outside temperature."""
        heating_curve_value = self._get_heating_curve_value(
            target_temperature=target_temperature,
            outside_temperature=outside_temperature
        )

        self._last_heating_curve_value = round(self.base_offset + ((self._coefficient / 4) * heating_curve_value), 1)

    def calculate_coefficient(self, setpoint: float, target_temperature: float, outside_temperature: float) -> float:
        """Convert a setpoint to a coefficient value"""
        heating_curve_value = self._get_heating_curve_value(
            target_temperature=target_temperature,
            outside_temperature=outside_temperature
        )

        return round(4 * (setpoint - self.base_offset) / heating_curve_value, 1)

    def autotune(self, setpoint: float, target_temperature: float, outside_temperature: float):
        if setpoint <= MINIMUM_SETPOINT:
            return

        coefficient = self.calculate_coefficient(
            setpoint=setpoint,
            target_temperature=target_temperature,
            outside_temperature=outside_temperature
        )

        if coefficient != self._optimal_coefficient:
            self._optimal_coefficients.append(coefficient)

        self._optimal_coefficient = coefficient

    @staticmethod
    def _get_heating_curve_value(target_temperature: float, outside_temperature: float) -> float:
        """Calculate the heating curve value based on the current outside temperature"""
        return target_temperature - (0.01 * outside_temperature ** 2) - (0.8 * outside_temperature)

    @property
    def optimal_coefficient(self):
        if len(self._optimal_coefficients) == 0:
            return None

        return round(mean(self._optimal_coefficients), 1)

    @property
    def base_offset(self) -> float:
        """Determine the base offset for the heating system."""
        return 20 if self._heating_system == HEATING_SYSTEM_UNDERFLOOR else 27.2

    @property
    def value(self):
        return self._last_heating_curve_value
