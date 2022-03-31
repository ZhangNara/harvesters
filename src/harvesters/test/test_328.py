#!/usr/bin/env python3
# ----------------------------------------------------------------------------
#
# Copyright 2022 EMVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ----------------------------------------------------------------------------


# Standard library imports
from enum import Enum
import os
import unittest

# Related third party imports
from harvesters.core import Harvester, ImageAcquirer

# Local application/library specific imports
from harvesters.test.base_harvester import get_cti_file_path


class Variable(Enum):
    TEST_TARGET = 1
    LOGGING_CONFIG = 2
    LOG_BUFFER = 3


variable_dit = {
    Variable.TEST_TARGET: 'HARVESTERS_TEST_TARGET',
    Variable.LOGGING_CONFIG: 'HARVESTERS_LOGGING_CONFIG',
    Variable.LOG_BUFFER: 'HARVESTERS_LOG_BUFFER',
}


class Test328(unittest.TestCase):
    def check(self):
        for name in variable_dit.values():
            if name not in os.environ:
                self.skipTest(reason="missing a required variable")

    @staticmethod
    def get_cti_file_path():
        return os.getenv(variable_dit.get(Variable.TEST_TARGET))

    def setUp(self) -> None:
        self.check()
        self.cti_file_path = get_cti_file_path()
        self.harvester = Harvester()
        self.harvester.add_file(self.cti_file_path)
        self.harvester.update()
        self.assertTrue(len(self.harvester.device_info_list) > 0)
        self.ias = []

    def tearDown(self) -> None:
        for ia in self.ias:
            ia.destroy()
        self.harvester.reset()

    def test_multiple_image_acquisition(self):
        nr_devices = len(self.harvester.device_info_list)
        for i in range(nr_devices):
            self.ias.append(self.harvester.create(i))

        for ia in self.ias:  # type: ImageAcquirer
            ia.start(run_as_thread=True)

        counters = [0] * nr_devices
        nr_images = 10

        while not all(counter > nr_images for counter in counters):
            for i, ia in enumerate(self.ias):  # type: int, ImageAcquirer
                with ia.fetch() as _:
                    counters[i] += 1


if __name__ == '__main__':
    unittest.main()
