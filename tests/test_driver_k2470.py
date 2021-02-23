import unittest
import random

from comet.resource import Resource
from comet.driver import Driver

from comet.driver.keithley import K2470

from .test_driver import BaseDriverTest

class K2470Test(BaseDriverTest):

    driver_type = K2470

    def test_beeper(self):
        for value in (True, False, 1, 0):
            self.resource.buffer = ['1']
            self.driver.beeper = value
            self.assertEqual(self.resource.buffer, [f'beeper = {value:d}', 'waitcomplete()', 'print([[1]])'])

            self.resource.buffer = [f'{value:d}']
            self.assertEqual(self.driver.beeper, value)
            self.assertEqual(self.resource.buffer, ['print(beeper)'])

    def test_source_autorange(self):
        for value in (True, False, 1, 0):
            self.resource.buffer = ['1']
            self.driver.source.autorange = value
            self.assertEqual(self.resource.buffer, [f'smu.source.autorange = {value:d}', 'waitcomplete()', 'print([[1]])'])

            self.resource.buffer = [f'{value:d}']
            self.assertEqual(self.driver.source.autorange, value)
            self.assertEqual(self.resource.buffer, ['print(smu.source.autorange)'])

    def test_source_autodelay(self):
        for value in (True, False, 1, 0):
            self.resource.buffer = ['1']
            self.driver.source.autodelay = value
            self.assertEqual(self.resource.buffer, [f'smu.source.autodelay = {value:d}', 'waitcomplete()', 'print([[1]])'])

            self.resource.buffer = [f'{value:d}']
            self.assertEqual(self.driver.source.autodelay, value)
            self.assertEqual(self.resource.buffer, ['print(smu.source.autodelay)'])

    def test_source_delay(self):
        for value in (0, 3, 0.42):
            self.resource.buffer = ['1']
            self.driver.source.delay = value
            self.assertEqual(self.resource.buffer, [f'smu.source.delay = {value:E}', 'waitcomplete()', 'print([[1]])'])

            self.resource.buffer = [f'{value:E}']
            self.assertEqual(self.driver.source.delay, value)
            self.assertEqual(self.resource.buffer, ['print(smu.source.delay)'])

    def test_source_output(self):
        for value in (True, False, 1, 0):
            self.resource.buffer = ['1']
            self.driver.source.output = value
            self.assertEqual(self.resource.buffer, [f'smu.source.output = {value:d}', 'waitcomplete()', 'print([[1]])'])

            self.resource.buffer = [f'{value:d}']
            self.assertEqual(self.driver.source.output, value)
            self.assertEqual(self.resource.buffer, ['print(smu.source.output)'])

    def test_source_protect_tripped(self):
        for value in (True, False, 1, 0):
            self.resource.buffer = [f'{value:d}']
            self.assertEqual(self.driver.source.protect.tripped, value)
            self.assertEqual(self.resource.buffer, ['print(smu.source.protect.tripped)'])

if __name__ == '__main__':
    unittest.main()
