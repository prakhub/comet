import pytest

from comet.driver.siemens import Logo8

from math import log10


class MockResource:

    def __init__(self):
        self.buffer = {}

    def clear(self): ...  # VISA bus clear

    def read(self):
        return self.buffer.pop(0)

    def write(self, address, message):
        if address not in self.buffer:
            self.buffer[address] = []

        self.buffer[address].append(message)

    def read(self, address):
        return self.buffer[address].pop(0)


@pytest.fixture
def resource():
    return MockResource()


@pytest.fixture
def driver(resource):
    return Logo8(resource)


def test_identify(driver, resource):
    resource.pointer = "c_void_p(2933217896576)"
    assert driver.identify() == "Logo!8 pointer at c_void_p(2933217896576)"


def test_read_gauge_pressure(driver, resource):
    resource.buffer = {"VW1118": [100]}

    assert abs(driver.gauge_pressure - 10 ** (1 - 5.5)) < 1e-10
    assert resource.buffer == {"VW1118": []}


def test_read_valve_voltage(driver, resource):
    resource.buffer = {"VW1122": [500]}

    assert driver.valve_voltage == 5
    assert resource.buffer == {"VW1122": []}


def test_set_valve_voltage(driver, resource):

    driver.valve_voltage = 0.5

    buff = resource.buffer["VW1122"]
    assert len(buff) == 1
    assert buff.pop(0) == 50


def test_set_pressure_setpoint(driver, resource):

    driver.pressure_setpoint = 0.1  # mbar

    buff = resource.buffer["VW1120"]
    assert len(buff) == 1
    assert buff.pop(0) == round(((5.5 + log10(0.1)) * 100), 0)


def test_read_pressure_setpoint(driver, resource):

    resource.buffer = {"VW1120": [100]}

    pressure_setpoint = driver.pressure_setpoint

    assert abs(pressure_setpoint - 10 ** (1 - 5.5)) < 1e10
    assert resource.buffer == {"VW1120": []}


def test_close_valve(driver, resource):
    driver.close_valve()

    buff = resource.buffer["VW1122"]
    assert len(buff) == 1
    assert buff.pop(0) == 0


def test_open_valve(driver, resource):

    driver.open_valve()

    buff = resource.buffer["VW1122"]
    assert len(buff) == 1
    assert buff.pop(0) == 1000
