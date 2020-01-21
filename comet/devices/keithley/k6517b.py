from comet.devices import IEC60488

__all__ = ['K6517B']

class K6517B(IEC60488):
    """Keithley Model 6517B Electrometer."""

    options = {
        "read_termination": "\r"
    }
