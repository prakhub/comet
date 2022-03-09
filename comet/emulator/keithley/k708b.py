from comet.emulator import message
from comet.utils import combine_matrix
from comet.emulator import register_emulator

from .k707b import K707BEmulator


@register_emulator('keithley.k708b')
class K708BEmulator(K707BEmulator):

    IDENTITY = "Keithley Inc., Model 708B, 43768438, v1.0 (Emulator)"
    CHANNELS = combine_matrix('1', 'ABCDEFGH', '0', '12345678')
