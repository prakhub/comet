import datetime
from collections import namedtuple

from comet import Device

__all__ = ['ITC']

class ITC(Device):
    """Interface for CTS Climate Chambers."""

    AnalogChannels = {
        1: b'A0',
        2: b'A1',
        3: b'A2',
        4: b'A3',
        5: b'A4',
        6: b'A5',
        7: b'A6',
        8: b'A7',
        9: b'A8',
        10: b'A9',
        11: b'A:',
        12: b'A;',
        13: b'A<',
        14: b'A=',
        15: b'A>',
        16: b'A?',
    }
    """Mapping analog channel index to channel code. When writing convert to
    lower case."""

    WarningMessages = {
        '\x01': "Wassernachfüllen",
        '\x02': "Temp. Toleranzband Oben",
        '\x03': "Temp. Toleranzband Unten",
        '\x04': "Feuchte Toleranzband Oben",
        '\x05': "Feuchte Toleranzband Unten",
        '\x06': "Wasserbad Abschlaemmen",
    }
    """Warning messages."""

    ErrorMessages = {
        '\x31': "Temperatur Grenze Min 08-B1",
        '\x32': "Temperatur Grenze Max 08-B1",
        '\x33': "Temp. Begrenzer Pruefr. 01-F1.1",
        '\x34': "TK Vent. Pruefr. 02-F2.1",
        '\x35': "Pruefgutschutz Max 09-A1",
        '\x37': "Ueberdruck Kuehlung 03-B40",
        '\x38': "Feuchtegrenze Min 08-B2",
        '\x39': "Feuchtegrenze Max 08-B2",
        '\x3a': "Feuchtesensor 08-B2",
        '\x3b': "Wassermangel Feuchte 07-B80",
        '\x3c': "TK Ventilator Verfl. 03-F5.1",
        '\x3d': "Siededrucksensor 03-B60",
        '\x3f': "Pt100 Abluft 08-B1.1",
        '\x40': "Pt100 Zuluft 08-B1.2",
        '\x41': "Pt100 Wasserbad 07-B4",
        '\x42': "Schwimmer Wasservorrat 07-B81",
        '\x43': "Pt100 Beweglich 08-B15",
        '\x47': "Pt100 Sauggas K 03-B13",
        '\x4b': "Sauggastemp. K 03-B13",
        '\x53': "Absaugung Kuehlung 03-B43",
        '\x5b': "Schwimmer Wasserbad 07-B80",
        '\x5c': "Pt100 Saugdampf K 03-B12",
        '\x5e': "Siededrucksensor K 03-B43",
        '\x62': "Leistungsschalter Einspeisung 00-Q1",
    }
    """Error messages."""

    Status = namedtuple('Status', ('running', 'warning', 'error', 'channels'))

    def query_bytes(self, message, count):
        """Raw query for bytes.

        >>> device.query_bytes('P', 4)
        'P001'
        """
        with self.lock:
            if not isinstance(message, bytes):
                message = message.encode()
            self.resource.write_raw(message)
            return self.resource.read_bytes(count).decode()

    @property
    def time(self) -> object:
        """Returns current date and time of device as datetime object.

        >>> device.time
        datetime.datetime(2019, 6, 12, 13, 01, 21)
        """
        result = self.query_bytes('T', 13)
        return datetime.datetime.strptime(result, 'T%d%m%y%H%M%S')

    @time.setter
    def time(self, dt) -> None:
        """Update device date and time, returns updated data and time as datetime object.

        >>> device.time = datetime.now()
        """
        datetime_format = 't%d%m%y%H%M%S'
        result = self.query_bytes(dt.strftime(datetime_format), 13)
        if dt != datetime.datetime.strptime(result, datetime_format):
            raise RuntimeError("failed to set date and time")

    def analog_channel(self, index):
        """Read analog channel, returns tuple containing actual value and target value.
        >>> device.analogChannel(1) # read temperature target/actual
        (24.5, 25.0)
        """
        code = self.AnalogChannels[index]
        result, actual, target = self.query_bytes(code, 14).split()
        if result != code.decode():
            raise RuntimeError("invalid channel returned: '{}'".format(result))
        return float(actual), float(target)

    def set_analog_channel(self, index, value):
        """Set target value for analog channel.
        >>> device.set_analog_channel(1, 42.0)
        """
        if not 1 <= index <= 7:
            raise ValueError("invalid channel number: '{}'".format(index))
        code = self.AnalogChannels[index].lower().decode() # write requires lower case 'a'
        result = self.query_bytes("{} {:05.1f}".format(code, value), 1)
        if result != 'a':
            raise RuntimeError("failed to set target for channel '{}'".format(index))

    @property
    def status(self) -> object:
        """Returns device status as object.

        >>> device.status
        Status(running=False, warning=None, error=None, channels={})
        """
        result = self.query_bytes('S', 10)
        running = bool(int(result[1]))
        is_error = bool(int(result[2]))
        channels = {channel: bool(int(state)) for channel, state in enumerate(result[3:9])}
        error_nr = result[9]
        warning = self.WarningMessages[error_nr] if is_error and error_nr in self.WarningMessages else None
        error = self.ErrorMessages[error_nr] if is_error and error_nr in self.ErrorMessages else None
        return self.Status(running, warning, error, channels)

    @property
    def error_message(self) -> str:
        """Returns current error message.

        >>> device.error_message
        'Wasserbad Abschlaemmen'
        """
        result = self.query_bytes('F', 33)
        return result[1:].strip()

    @property
    def program(self) -> int:
        """Returns number of running program or 0 if no program is running.

        >>> device.program
        42
        """
        result = self.query_bytes('P', 4)
        return int(result[1:])

    @program.setter
    def program(self, number: int) -> None:
        """Starts a program. Returns program number or 0 for no program.

        >>> device.program = 42
        """
        result = self.query_bytes(f'P{number:03d}', 4)
        if number != int(result[1:]):
            raise RuntimeError(f"failed to start program '{number}'")

    def start(self) -> None:
        """Switch climate chamber ON.

        >>> device.start()
        """
        result = self.query_bytes('s1 1', 2)
        if result != 's1':
            raise RuntimeError("failed to start instrument")

    def stop(self) -> None:
        """Switch climate chamber OFF.

        >>> device.stop()
        """
        result = self.query_bytes('s1 0', 2)
        if result != 's1':
            raise RuntimeError("failed to stop instrument")
