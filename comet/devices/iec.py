from comet import Device

__all__ = ['IEC60488']

class IEC60488(Device):
    """IEC60488 compatible device."""

    def identification(self):
        """Returns IEC60488 device identification."""
        return self.resource().query('*IDN?')

    def reset(self):
        """Reset IEC60488 device."""
        return self.resource().write('*RST')

    def opc(self):
        return self.resource().write('*OPC?')
