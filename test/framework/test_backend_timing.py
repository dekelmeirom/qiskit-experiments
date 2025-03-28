# This code is part of Qiskit.
#
# (C) Copyright IBM 2021.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""Tests for BackendTiming."""

from test.base import QiskitExperimentsTestCase

from ddt import data, ddt, unpack
from qiskit import QiskitError
from qiskit_ibm_runtime.fake_provider import FakeNairobiV2

from qiskit_experiments.framework import BackendTiming


@ddt
class TestBackendTiming(QiskitExperimentsTestCase):
    """Test BackendTiming"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.dt = 1 / 4.5e9
        cls.granularity = 16

    def setUp(self):
        super().setUp()
        # Creating a complete fake backend is difficult so we use one from
        # qiskit. Just to be safe, we override hardware properties
        # with the values assumed for the unit tests.
        self.backend = FakeNairobiV2()
        self.backend.target.dt = self.dt
        self.backend.target.granularity = self.granularity

    @data((True, "s"), (False, "dt"))
    @unpack
    def test_delay_unit(self, null_dt, result):
        """Test delay unit matches dt"""
        if null_dt:
            self.backend.target.dt = None
        timing = BackendTiming(self.backend)
        self.assertEqual(timing.delay_unit, result)

    def test_round_delay_args(self):
        """Test argument checking in round_delay"""
        timing = BackendTiming(self.backend)
        with self.assertRaises(QiskitError):
            timing.round_delay(time=self.dt * 16, samples=16)
        with self.assertRaises(QiskitError):
            timing.round_delay()

    @data([14, 16], [16, 16], [18, 16], [64.5, 64])
    @unpack
    def test_round_delay(self, samples_in, samples_out):
        """Test delay calculation with time input"""
        time = self.dt * samples_in

        timing = BackendTiming(self.backend)
        self.assertEqual(timing.round_delay(time=time), samples_out)

    def test_round_delay_no_dt(self):
        """Test delay when dt is None"""
        time = self.dt * 16

        self.backend.target.dt = None
        timing = BackendTiming(self.backend)
        self.assertEqual(timing.round_delay(time=time), time)

    @data([14, 16], [16, 16], [18, 16], [64.5, 64])
    @unpack
    def test_round_delay_samples_in(self, samples_in, samples_out):
        """Test delay calculation with samples input"""
        timing = BackendTiming(self.backend)
        self.assertEqual(timing.round_delay(samples=samples_in), samples_out)

    def test_delay_time(self):
        """Test delay_time calculation"""
        time_in = self.dt * 16.1
        time_out = self.dt * 16

        timing = BackendTiming(self.backend)
        self.assertAlmostEqual(timing.delay_time(time=time_in), time_out, delta=1e-6 * self.dt)

    def test_delay_time_samples_in(self):
        """Test delay_time calculation"""
        samples_in = 16.1
        time_out = self.dt * 16

        timing = BackendTiming(self.backend)
        self.assertAlmostEqual(
            timing.delay_time(samples=samples_in), time_out, delta=1e-6 * self.dt
        )

    def test_delay_time_no_dt(self):
        """Test delay time calculation when dt is None"""
        time_in = self.dt * 16.1
        time_out = time_in

        self.backend.target.dt = None
        timing = BackendTiming(self.backend)
        self.assertAlmostEqual(timing.delay_time(time=time_in), time_out, delta=1e-6 * self.dt)
