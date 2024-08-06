from comet.driver import Driver
from typing import Dict, Optional

from math import log10

__all__ = ["Logo8"]


LOGO_ADRESSES: Dict[str, str] = {
    "pressure_gauge": "VW1118",
    "needle_valve": "VW1122",
    "pressure_setpoint": "VW1120",
}


def voltage_to_pressure(voltage: float) -> float:
    """Convert voltage measured by RPT200 gauge to mbar

    Args:
        voltage (float): Measured voltage in Volts

    Returns:
        float: Pressure in mbar
    """
    return 10 ** (voltage - 5.5)


def pressure_to_voltage(pressure: float) -> float:
    """Convert pressure in mbar to voltage for RPT200 gauge

    Args:
        pressure (float): Pressure in mbar

    Returns:
        float: Voltage in Volts
    """
    return round(5.5 + log10(pressure), 0)


class Logo6(Driver):

    def read(self, address: str) -> float:
        """Read analog value from memory bank in Logo!8 PLC"""
        return self.resource.read(address) / 1000 * 10

    def write(self, address: str, value: float) -> None:
        """Write analog value to memory bank in Logo!8 PLC"""
        # Clamp value to 0-10V
        value = max(0, min(10, value))

        self.resource.write(address, value * 1000 / 10)

    @property
    def gauge_pressure(self):
        """Get pressure measured by RPT200 gauge in mbar"""

        gauge_voltage = self.resource.read(LOGO_ADRESSES["pressure_gauge"])

        return voltage_to_pressure(gauge_voltage)

    @property
    def valve_voltage(self):
        """Get PID needle valve control voltage in Volts"""

        return self.resource.read(LOGO_ADRESSES["needle_valve"])

    @valve_voltage.setter
    def valve_voltage(self, voltage: float):
        """Set PID needle valve control voltage in Volts"""

        self.resource.write(LOGO_ADRESSES["needle_valve"], voltage)

    @property
    def pressure_setpoint(self):
        """Get PID pressure setpoint in mbar"""

        setpoint_voltage = self.resource.read(LOGO_ADRESSES["pressure_setpoint"])

        return voltage_to_pressure(setpoint_voltage)

    @pressure_setpoint.setter
    def pressure_setpoint(self, pressure: float):
        """Set PID pressure setpoint in mbar"""

        setpoint_voltage = pressure_to_voltage(pressure)

        self.resource.write(LOGO_ADRESSES["pressure_setpoint"], setpoint_voltage)

    def close_valve(self):
        """Completely shut needle valve (0V)"""
        self.resource.write(LOGO_ADRESSES["needle_valve"], 0.0)

    def open_valve(self):
        """Completely open needle valve (10V)"""
        self.resource.write(LOGO_ADRESSES["needle_valve"], 10.0)

    def identify(self):
        """Acquire Identifcation string"""

        pointer = self.resource.pointer

        return f"Logo!8 pointer at {pointer}"
