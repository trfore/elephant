# -*- coding: utf-8 -*-
"""
Unit tests for the signal_proc module of elephant.

:copyright: Copyright 2014 by the Elephant team, see AUTHORS.txt.
:license: Modified BSD, see LICENSE.txt for details.
"""
from __future__ import division, print_function
import unittest

import neo
import numpy as np
import scipy.stats
from numpy.testing.utils import assert_array_almost_equal
import quantities as pq

import elephant.signal_proc as es
from numpy.ma.testutils import assert_array_equal


class ZscoreTestCase(unittest.TestCase):
    def setUp(self):
        self.test_seq1 = [1, 28, 4, 47, 5, 16, 2, 5, 21, 12,
                          4, 12, 59, 2, 4, 18, 33, 25, 2, 34,
                          4, 1, 1, 14, 8, 1, 10, 1, 8, 20,
                          5, 1, 6, 5, 12, 2, 8, 8, 2, 8,
                          2, 10, 2, 1, 1, 2, 15, 3, 20, 6,
                          11, 6, 18, 2, 5, 17, 4, 3, 13, 6,
                          1, 18, 1, 16, 12, 2, 52, 2, 5, 7,
                          6, 25, 6, 5, 3, 15, 4, 3, 16, 3,
                          6, 5, 24, 21, 3, 3, 4, 8, 4, 11,
                          5, 7, 5, 6, 8, 11, 33, 10, 7, 4]
        self.test_seq2 = [6, 3, 0, 0, 18, 4, 14, 98, 3, 56,
                          7, 4, 6, 9, 11, 16, 13, 3, 2, 15,
                          24, 1, 0, 7, 4, 4, 9, 24, 12, 11,
                          9, 7, 9, 8, 5, 2, 7, 12, 15, 17,
                          3, 7, 2, 1, 0, 17, 2, 6, 3, 32,
                          22, 19, 11, 8, 5, 4, 3, 2, 7, 21,
                          24, 2, 5, 10, 11, 14, 6, 8, 4, 12,
                          6, 5, 2, 22, 25, 19, 16, 22, 13, 2,
                          19, 20, 17, 19, 2, 4, 1, 3, 5, 23,
                          20, 15, 4, 7, 10, 14, 15, 15, 20, 1]

    def test_zscore_single_dup(self):
        '''
        Test zscore on a single AnalogSignal, asking to return a duplicate.
        '''
        signal = neo.AnalogSignal(
            self.test_seq1, units='mV',
            t_start=0.*pq.ms, sampling_rate=1000.*pq.Hz, dtype=float)

        m = np.mean(self.test_seq1)
        s = np.std(self.test_seq1)
        target = (self.test_seq1 - m) / s
        assert_array_equal(target, scipy.stats.zscore(self.test_seq1))

        result = es.zscore(signal, inplace=False)
        assert_array_almost_equal(
            result.magnitude, target, decimal=9)

        self.assertEqual(result.units, pq.Quantity(1. * pq.dimensionless))

        # Assert original signal is untouched
        self.assertEqual(signal[0].magnitude, self.test_seq1[0])

    def test_zscore_single_inplace(self):
        '''
        Test z-score on a single AnalogSignal, asking for an inplace operation.
        '''
        signal = neo.AnalogSignal(
            self.test_seq1, units='mV',
            t_start=0.*pq.ms, sampling_rate=1000.*pq.Hz, dtype=float)

        m = np.mean(self.test_seq1)
        s = np.std(self.test_seq1)
        target = (self.test_seq1 - m) / s

        result = es.zscore(signal, inplace=True)

        assert_array_almost_equal(
            result.magnitude, target, decimal=9)

        self.assertEqual(result.units, pq.Quantity(1. * pq.dimensionless))

        # Assert original signal is overwritten
        self.assertEqual(signal[0].magnitude, target[0])

    def test_zscore_single_multidim_dup(self):
        '''
        Test zscore on a single AnalogSignal with multiple dimensions, asking
        to return a duplicate.
        '''
        signal = neo.AnalogSignalArray(
            np.transpose(
                np.vstack([self.test_seq1, self.test_seq2])), units='mV',
            t_start=0.*pq.ms, sampling_rate=1000.*pq.Hz, dtype=float)

        m = np.mean(signal.magnitude, axis=0, keepdims=True)
        s = np.std(signal.magnitude, axis=0, keepdims=True)
        target = (signal.magnitude - m) / s

        assert_array_almost_equal(
            es.zscore(
                signal, inplace=False).magnitude, target, decimal=9)

        # Assert original signal is untouched
        self.assertEqual(signal[0, 0].magnitude, self.test_seq1[0])

    def test_zscore_single_multidim_inplace(self):
        '''
        Test z-score on a single AnalogSignal with multiple dimensions, asking
        for an inplace operation.
        '''
        signal = neo.AnalogSignalArray(
            np.vstack([self.test_seq1, self.test_seq2]), units='mV',
            t_start=0.*pq.ms, sampling_rate=1000.*pq.Hz, dtype=float)

        m = np.mean(signal.magnitude, axis=0, keepdims=True)
        s = np.std(signal.magnitude, axis=0, keepdims=True)
        target = (signal.magnitude - m) / s

        assert_array_almost_equal(
            es.zscore(
                signal, inplace=True).magnitude, target, decimal=9)

        # Assert original signal is overwritten
        self.assertEqual(signal[0, 0].magnitude, target[0, 0])

    def test_zscore_single_dup_int(self):
        '''
        Test if the z-score is correctly calculated even if the input is an
        AnalogSignal of type int, asking for a duplicate (duplicate should be
        of type float).
        '''
        signal = neo.AnalogSignal(
            self.test_seq1, units='mV',
            t_start=0.*pq.ms, sampling_rate=1000.*pq.Hz, dtype=int)

        m = np.mean(self.test_seq1)
        s = np.std(self.test_seq1)
        target = (self.test_seq1 - m) / s

        assert_array_almost_equal(
            es.zscore(signal, inplace=False).magnitude,
            target, decimal=9)

        # Assert original signal is untouched
        self.assertEqual(signal.magnitude[0], self.test_seq1[0])

    def test_zscore_single_inplace_int(self):
        '''
        Test if the z-score is correctly calculated even if the input is an
        AnalogSignal of type int, asking for an inplace operation
        (should be int?).
        '''
        signal = neo.AnalogSignal(
            self.test_seq1, units='mV',
            t_start=0.*pq.ms, sampling_rate=1000.*pq.Hz, dtype=int)

        m = np.mean(self.test_seq1)
        s = np.std(self.test_seq1)
        target = (self.test_seq1 - m) / s

        assert_array_almost_equal(
            es.zscore(signal, inplace=True).magnitude,
            target.astype(int), decimal=9)

        # Assert original signal is overwritten
        self.assertEqual(signal[0].magnitude, target.astype(int)[0])

    def test_zscore_list_dup(self):
        '''
        Test zscore on a list of AnalogSignalArray objects, asking to return a
        duplicate.
        '''
        signal1 = neo.AnalogSignalArray(
            np.transpose(np.vstack([self.test_seq1, self.test_seq1])),
            units='mV',
            t_start=0.*pq.ms, sampling_rate=1000.*pq.Hz, dtype=float)
        signal2 = neo.AnalogSignalArray(
            np.transpose(np.vstack([self.test_seq1, self.test_seq2])),
            units='mV',
            t_start=0.*pq.ms, sampling_rate=1000.*pq.Hz, dtype=float)
        signal_list = [signal1, signal2]

        m = np.mean(np.hstack([self.test_seq1, self.test_seq1]))
        s = np.std(np.hstack([self.test_seq1, self.test_seq1]))
        target11 = (self.test_seq1 - m) / s
        target21 = (self.test_seq1 - m) / s
        m = np.mean(np.hstack([self.test_seq1, self.test_seq2]))
        s = np.std(np.hstack([self.test_seq1, self.test_seq2]))
        target12 = (self.test_seq1 - m) / s
        target22 = (self.test_seq2 - m) / s

        # Call elephant function
        result = es.zscore(signal_list, inplace=False)

        assert_array_almost_equal(
            result[0].magnitude,
            np.transpose(np.vstack([target11, target12])), decimal=9)
        assert_array_almost_equal(
            result[1].magnitude,
            np.transpose(np.vstack([target21, target22])), decimal=9)

        # Assert original signal is untouched
        self.assertEqual(signal1.magnitude[0, 0], self.test_seq1[0])
        self.assertEqual(signal2.magnitude[0, 1], self.test_seq2[0])

    def test_zscore_list_inplace(self):
        '''
        Test zscore on a list of AnalogSignalArray objects, asking for an
        inplace operation.
        '''
        signal1 = neo.AnalogSignalArray(
            np.transpose(np.vstack([self.test_seq1, self.test_seq1])),
            units='mV',
            t_start=0.*pq.ms, sampling_rate=1000.*pq.Hz, dtype=float)
        signal2 = neo.AnalogSignalArray(
            np.transpose(np.vstack([self.test_seq1, self.test_seq2])),
            units='mV',
            t_start=0.*pq.ms, sampling_rate=1000.*pq.Hz, dtype=float)
        signal_list = [signal1, signal2]

        m = np.mean(np.hstack([self.test_seq1, self.test_seq1]))
        s = np.std(np.hstack([self.test_seq1, self.test_seq1]))
        target11 = (self.test_seq1 - m) / s
        target21 = (self.test_seq1 - m) / s
        m = np.mean(np.hstack([self.test_seq1, self.test_seq2]))
        s = np.std(np.hstack([self.test_seq1, self.test_seq2]))
        target12 = (self.test_seq1 - m) / s
        target22 = (self.test_seq2 - m) / s

        # Call elephant function
        result = es.zscore(signal_list, inplace=True)

        assert_array_almost_equal(
            result[0].magnitude,
            np.transpose(np.vstack([target11, target12])), decimal=9)
        assert_array_almost_equal(
            result[1].magnitude,
            np.transpose(np.vstack([target21, target22])), decimal=9)

        # Assert original signal is overwritten
        self.assertEqual(signal1[0, 0].magnitude, target11[0])
        self.assertEqual(signal2[0, 0].magnitude, target21[0])


if __name__ == '__main__':
    unittest.main()
