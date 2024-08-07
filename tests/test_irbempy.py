#!/usr/bin/env	python
# -*- coding: utf-8 -*-
"""
testing	the	irbempy	module

Copyright 2010-2012 Los Alamos National Security, LLC.
"""

import unittest
import spacepy_testing
import spacepy
import spacepy.omni
import spacepy.time
import spacepy.coordinates
try:
    import spacepy.irbempy as ib
except ImportError:  # if IRBEM fails, test suite should not break entirely...
    pass
import datetime
import numpy as np
import numpy.testing
from numpy import array

__all__ = ['IRBEMBigTests', 'IRBEMTestsWithoutOMNI', 'IRBEMShieldoseTests']


class IRBEMBigTests(unittest.TestCase):

    def setUp(self):
        self.ticks = spacepy.time.Ticktock(['2001-02-02T12:00:00', '2001-02-02T12:10:00'], 'ISO')
        self.loci = spacepy.coordinates.Coords([[3,0,0],[2,0,0]], 'GEO', 'car', use_irbem=True)
        self.omnivals = spacepy.omni.get_omni(self.ticks, dbase='Test')

    def test_prep_ctypes(self):
        """Check prep_ctypes preserves original values of prep_irbem"""
        expected_arrays = {
            'degalpha': [0.0] * 25,
            'idoysat': [33.0] * 2 + [0.0] * 99998,
            'iyearsat': [2001.] * 2 + [0.0] * 99998,
            'xin3': [0.0] * 100000,
            'xin2': [0.0] * 100000,
            'xin1': [3., 2.] + [0.0] * 99998,
            'utsat': [43200., 43800.] + [0.0] * 99998,
            }
        expected_scalars = {
            'sysaxes': 1,
            'kext': 10,
        }
        d = ib.prep_irbem(self.ticks, self.loci, omnivals=self.omnivals)
        actual = ib.prep_ctypes(d)
        for key in expected_arrays:
            numpy.testing.assert_almost_equal(expected_arrays[key],
                                              actual[key].contents,
                                              decimal=5)
        for key in expected_scalars:
            numpy.testing.assert_almost_equal(expected_scalars[key],
                                              actual[key].value,
                                              decimal = 5)
        numpy.testing.assert_almost_equal([1, 0, 0, 0, 0], actual['options'])


    def test_prep_irbem(self):
        expected = {
            'badval': -1e31,
            'degalpha': [0.0] * 25,
            'idoysat': [33.0] * 2 + [0.0] * 99998,
            'ntime_max': 100000,
            'nalp_max': 25,
            'magin': np.zeros((25, 100000)),
            'sysaxes': 1,
            'kext': 10,
            'iyearsat': [2001.] * 2 + [0.0] * 99998,
            'xin3': 0.0 * 100000,
            'xin2': 0.0 * 100000,
            'xin1': [3., 2.] + [0.0] * 99998,
            'utsat': [43200., 43800.] + [0.0] * 99998,
            'options': [1, 0, 0, 0, 0],
            }
        expected['magin'][:, :2] = array(
            [[  3.00000012e+00,   3.00000012e+00],
             [ -9.00000000e+00,  -9.00000000e+00],
             [  3.20000005e+00,   3.15000006e+00],
             [  3.96000000e+02,   3.96000000e+02],
             [  1.07000005e+00,   1.05500005e+00],
             [  2.00000003e-01,  -4.99999917e-02],
             [ -1.00000001e-01,   1.33333326e-01],
             [  9.99999978e-03,   9.99999978e-03],
             [  2.99999993e-02,   2.49999994e-02],
             [  9.99999978e-03,   8.33333313e-03],
             [  2.60000005e-02,   2.46666670e-02],
             [  1.70000009e-02,   1.56666674e-02],
             [  3.16000015e-01,   3.14333344e-01],
             [  6.00000005e-03,   5.50000004e-03],
             [  1.70000009e-02,   1.50000007e-02],
             [  2.19999999e-02,   1.98333332e-02],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00],
             [  0.00000000e+00,   0.00000000e+00]])

        actual = ib.prep_irbem(self.ticks, self.loci, omnivals=self.omnivals)
        for key in expected:
            numpy.testing.assert_almost_equal(expected[key],
                                              actual[key],
                                              decimal=5)
    def test_prep_irbem_sph_coords(self):
        """Test prep_irbem with spherical coordinate input"""
        loci = spacepy.coordinates.Coords([[3,0,0],[2,0,0]], 'GDZ', 'sph', use_irbem=True)
        # The rest is captured by previous test
        expected = {
            'xin1': [3.0, 2.0] + [0] * 99998,
            'degalpha': [10, 50] + [0] * 23
        }
        actual = ib.prep_irbem(self.ticks, loci, alpha=[10, 50], omnivals=self.omnivals)
        for key in expected:
            numpy.testing.assert_allclose(expected[key], actual[key])

    def test_prep_irbem_numeric_alpha(self):
        expected_nalpha = 1
        expected_degalpha = [45] + [0] * 24
        actual = ib.prep_irbem(self.ticks, self.loci, alpha=45, omnivals=self.omnivals)
        numpy.testing.assert_array_equal(expected_degalpha, actual['degalpha'])
        numpy.testing.assert_array_equal(expected_nalpha, actual['nalpha'])

    def test_prep_irbem_too_many_PA(self):
        """Call prep_irbem with too many pitch angles"""
        with self.assertRaises(ValueError) as cm:
            ib.prep_irbem(self.ticks, self.loci, numpy.arange(5, 180, 5),
                          omnivals=self.omnivals)
        self.assertEqual('Too many pitch angles requested; 25 is maximum.',
                         str(cm.exception))

    def test_find_Bmirror(self):
        expected = {'Blocal': array([ 1031.008992,  3451.98937]),
            'Bmirr': array([ 2495.243004,  8354.355467])}
        expected_loci = array([[2.194398006162409, -0.16398761258002298, 1.0628751496589137],
                           [1.397899531829991, 0.12422180881227743, -0.6473416588394351]])
        got = ib.find_Bmirror(self.ticks, self.loci, [40], omnivals=self.omnivals)
        for key in expected:
            numpy.testing.assert_almost_equal(expected[key], got[key], decimal=6)
        numpy.testing.assert_almost_equal(expected_loci, got['loci'].data, decimal=6)

    def test_find_Bmirror_multiple_PA(self):
        """Demonstrate find_Bmirror ignoring all pitch angles besides first

        Undesired behavior, will fail when find_Bmirror bug is fixed.
        """
        expected = {'Blocal': array([1031.00899203, 3451.98937044]),
                    'Bmirr': array([[1031.00899203, 1374.66281345, 1031.00899203, 34190.92088892],
                                    [3451.98937044, 4602.52051761, 3451.98937044, np.nan]])}
        expected_loci = array([[0.6632375457589057, -0.11317939661249253, 0.9116054568290045],
                               [np.nan, np.nan, np.nan]])
        got = ib.find_Bmirror(self.ticks, self.loci, [90, 60, 90, 10], omnivals=self.omnivals)
        for key in expected:
            numpy.testing.assert_almost_equal(expected[key], got[key], decimal=6)
        numpy.testing.assert_almost_equal(expected_loci, got['loci'].data)

    def test_find_LCDS(self):
        """test find_LCDS"""
        expected_numeric = {
            'LCDS': np.array([7.25101749, 7.36026469]),
            'K': np.array([0.05414297, 0.05167069]),
            'AlphaEq': np.array([45])}
        expected_utc = np.array([datetime.datetime(2001, 2, 2, 12, 0),
                                 datetime.datetime(2001, 2, 2, 12, 10)], dtype=object)
        actual = ib.find_LCDS(self.ticks, 45, omnivals=self.omnivals, bracket=[5, 10], tol=0.1)
        for key in expected_numeric:
            numpy.testing.assert_allclose(expected_numeric[key], actual[key])
        numpy.testing.assert_array_equal(expected_utc, actual['UTC'])

    def test_find_LCDS_multi_PA(self):
        """test find_LCDS with multiple pitch angles"""
        expected_numeric = {
            'LCDS': np.array([[7.25101749, 7.38250892]]),
            'K': np.array([[0.05414297, 0.03647328]]),
            'AlphaEq': np.array([45, 50])}
        expected_utc = np.array([datetime.datetime(2001, 2, 2, 12, 0)], dtype=object)
        actual = ib.find_LCDS(self.ticks[0], [45, 50], omnivals=self.omnivals, bracket=[5, 10], tol=0.1)
        for key in expected_numeric:
            numpy.testing.assert_allclose(actual[key], expected_numeric[key], rtol=1e-6)
        numpy.testing.assert_array_equal(actual['UTC'], expected_utc)

    def test_find_LCDS_badval(self):
        """test find_LCDS hitting badval"""
        # Bad inner bracket results in a ValueError
        with self.assertRaises(ValueError):
            ib.find_LCDS(self.ticks, 45, omnivals=self.omnivals, bracket=[100, 10])
        # Bad outer bracket just carries computation forward, regression test
        expected_bad_outer = {'LCDS': np.array([5.01071307, 4.99741893]),
                              'K': np.array([0.11522738, 0.11620084]),
                              'AlphaEq': np.array([45])}
        expected_utc = np.array([datetime.datetime(2001, 2, 2, 12, 0),
                                 datetime.datetime(2001, 2, 2, 12, 10)])
        # Huge tolerance because we don't need to spend forever hitting nans
        actual_bad_outer = ib.find_LCDS(self.ticks, 45, omnivals=self.omnivals, bracket=[5, -20], tol=1)
        for key, arr in expected_bad_outer.items():
            numpy.testing.assert_allclose(arr, expected_bad_outer[key], rtol=1e-6)
        numpy.testing.assert_array_equal(actual_bad_outer['UTC'], expected_utc)

    def test_find_LCDS_K(self):
        """test find_LCDS_K"""
        expected_numeric = {
            'LCDS': np.array([8.8919052 , 8.97300215]),
            'AlphaEq': np.array([90., 90.]),
            'K': np.array([1.5e-12])}
        expected_utc = np.array([datetime.datetime(2001, 2, 2, 12, 0),
                                 datetime.datetime(2001, 2, 2, 12, 10)], dtype=object)
        actual = ib.find_LCDS_K(self.ticks, 1.5e-12, extMag='T96', omnivals=self.omnivals, bracket=[5, 10], tol=0.1)
        for key in expected_numeric:
            numpy.testing.assert_allclose(expected_numeric[key], actual[key])
        numpy.testing.assert_array_equal(expected_utc, actual['UTC'])

    def test_find_LCDS_K_multi_K(self):
        """test find_LCDS_K with multiple K"""
        expected_numeric = {
                'LCDS': np.array([[7.828144, 7.828144],
                                  [7.724839, 7.724839]]),
                'AlphaEq': np.array([[90., 90.], [90., 90.]])}
        # Huge tolerance to speed up the test
        actual = ib.find_LCDS_K(self.ticks, [1.5e-12, 1.5e-12], extMag='T96',
                                omnivals=self.omnivals, bracket=[5, 10], tol=1)
        for key, arr in expected_numeric.items():
            numpy.testing.assert_allclose(arr, actual[key])

    def test_find_LCDS_K_badval(self):
        """test find_LCDS_K hitting badval"""
        actual_bad_inner = ib.find_LCDS_K(self.ticks, 1.5e-12, extMag='T96',
                                        omnivals=self.omnivals, bracket=[100, 10], tol=1)
        self.assertTrue(numpy.isnan(actual_bad_inner['LCDS']).all())

        expected_outer = np.array([5.06854355, 5.03953823])
        actual_bad_outer = ib.find_LCDS_K(self.ticks, 1.5e-12, extMag='T96',
                                          omnivals=self.omnivals, bracket=[5, 0], tol=1)
        numpy.testing.assert_allclose(expected_outer, actual_bad_outer['LCDS'])

    def test_find_LCDS_bad_bracket(self):
        """test find_LCDS and find_LCDS_K raise ValueError with invalid bracket"""
        with self.assertRaises(ValueError):
            ib.find_LCDS(self.ticks, 45, bracket=[1])
        with self.assertRaises(ValueError):
            ib.find_LCDS(self.ticks, 1.5e-12, bracket=[1])

    def test_find_magequator(self):
        expected = {'Bmin': array([ 1030.456337,  3444.077016 ])}
        Bmin_loci = array([[ 2.99935449,  0.005511 , -0.032353  ],
                          [ 2.00289871, -0.00734881,  0.045382]])
        actual = ib.find_magequator(self.ticks, self.loci, omnivals=self.omnivals)
        numpy.testing.assert_almost_equal(expected['Bmin'], actual['Bmin'], decimal=6)
        numpy.testing.assert_almost_equal(Bmin_loci, actual['loci'].data, decimal=6)

    def test_get_Bfield(self):
        """test get_Bfield"""
        expected = {'Blocal': array([ 1031.00899,  3451.98937]),
        'Bvec': array([[    3.49178,  -172.79037 ,  1016.4206],
                       [  335.0928,  -553.03591,  3390.88406]])}
        actual = ib.get_Bfield(self.ticks, self.loci, omnivals=self.omnivals)
        for key in expected.keys():
            numpy.testing.assert_almost_equal(actual[key], expected[key], decimal=5)

    def test_get_Lstar_T01(self):
        # test T01STORM
        expected = {'Xj': array([[ 0.000403], [ 0.00269002]]),
            'Lstar': array([[ 3.025887], [ 2.054195]]),
            'Bmirr': array([[ 1031.008992], [ 3451.98937]]),
            'Lm': array([[ 3.079151], [ 2.059326]]),
            'Bmin': array([ 1030.456337,  3444.077016 ]),
            'MLT': array([ 11.97159175,  12.13313906])}
        actual = ib.get_Lstar(self.ticks, self.loci, [90], omnivals=self.omnivals)
        for key in expected.keys():
            numpy.testing.assert_almost_equal(expected[key], actual[key], decimal=6)

    def test_get_Lstar_T05(self):
        # test T05
        expected = {'Xj': array([[ 0.266114], [ 0.186008]]),
                    'Lstar': array([[ 3.015461], [ 2.043043]]),
                    'Bmirr': array([[ 1150.670441], [ 3895.810805]]),
                    'Lm': array([[ 3.087026], [ 2.059734]]),
                    'Bmin': array([ 1015.468031,  3432.146907]),
                    'MLT': array([ 11.97159175,  12.13313906])}
        actual = ib.get_Lstar(self.ticks, self.loci, [70], extMag='T05', omnivals=self.omnivals)
        for key in expected:
            numpy.testing.assert_almost_equal(expected[key], actual[key], decimal=6)

    def test_get_Lstar_OPQuiet(self):
        # test OP-Quiet
        expected = {'Xj': array([[ 0.001051], [ 0.002722]]),
            'Lstar': array([[ 3.029621], [ 2.059631]]),
            'Blocal': array([ 1019.052401, 3467.52999]),
            'Lm': array([[ 3.091352], [ 2.056261]]),
            'Bmin': array([ 1018.669701,  3459.500966 ]),
            'MLT': array([ 11.97159175,  12.13313906])}
        actual = ib.get_Lstar(self.ticks, self.loci, [90], extMag="OPQUIET", omnivals=self.omnivals)
        for key in expected.keys():
            numpy.testing.assert_almost_equal(expected[key], actual[key], decimal=6)

    def test_get_Lstar_OPQuiet_multi(self):
        """Test Lstar on OPQ forcing multiprocess"""
        cpu_actual = spacepy.config['ncpus']
        # To trigger a worker pool, number of calcs must be
        # more than double number of cpus
        spacepy.config['ncpus'] = 4
        try:
            ticks = spacepy.time.tickrange(self.ticks.ISO[0], self.ticks.ISO[-1], 1/1440.)
            ncalc = len(ticks)  # Forced 10 times in test data range
            loci = spacepy.coordinates.Coords([[nc-4, 6-nc, 0] for nc in range(ncalc)], 'GEO', 'car', use_irbem=True)
            omnivals = spacepy.omni.get_omni(ticks, dbase='Test')
            expected = {'Lstar': array([[6.84698], [5.58814], [4.35608],
                                        [3.13613], [1.97344], [1.41439],
                                        [2.05375], [3.19979], [4.35920],
                                        [5.38242]]),
                        'Lm': array([[7.61427481], [6.13826804], [4.65907084],
                                     [3.21519241], [1.97225109], [1.41105356],
                                     [2.05626165], [3.28414042], [4.6531115 ],
                                     [5.92800457]])
                        }
            # OPQ won't use the OMNI, but if they're passed in
            # the code still processes them, so answers should be identical
            actuali= ib.get_Lstar(ticks, loci, [90], extMag="OPQUIET", omnivals=omnivals)
            actualn = ib.get_Lstar(ticks, loci, [90], extMag="OPQUIET", omnivals=None)
        finally:
            spacepy.config['ncpus'] = cpu_actual
        # Check that results are as expected
        numpy.testing.assert_almost_equal(expected['Lstar'], actuali['Lstar'], decimal=5)
        numpy.testing.assert_almost_equal(expected['Lm'], actuali['Lm'], decimal=5)
        numpy.testing.assert_almost_equal(expected['Lstar'], actualn['Lstar'], decimal=5)
        numpy.testing.assert_almost_equal(expected['Lm'], actualn['Lm'], decimal=5)

    def test_get_Lstar_TooManyPA(self):
        """test OP-Quiet with too many pitch angles"""
        with self.assertRaises(ValueError) as cm:
            ib.get_Lstar(
                self.ticks, self.loci, numpy.arange(5, 180, 5),
                extMag="OPQUIET", omnivals=self.omnivals)
        self.assertEqual('Too many pitch angles requested; 25 is maximum.',
                         str(cm.exception))

    def test_get_Lstar_landi2_shell_splitting(self):
        """test get_Lstar with landi2lstar and shell splitting options"""
        expected = {'Lm': array([[3.09135204, 3.09135204],
                                 [2.05626165, 2.05626165]]),
         'Lstar': array([[3.02418952, 3.02418952],[2.05327655, 2.05327655]]),
         'Bmirr': array([[1019.052401, 1019.052401],
                         [3467.52999008, 3467.52999008]]),
         'Bmin': array([1018.6697011 , 3459.50096553]),
         'Xj': array([[0.00105118, 0.00105118], [0.00272222, 0.00272222]]),
         'MLT': array([11.97159175, 12.13313906])}
        actual = ib.get_Lstar(self.ticks, self.loci, [90, 90], extMag='OPQUIET',
                              omnivals=self.omnivals, landi2lstar=True)
        for key in expected.keys():
            numpy.testing.assert_almost_equal(expected[key], actual[key], decimal=6)

    def test_get_Lstar_OPQuiet_landi2lstar(self):
        # test OP-Quiet with LandI2Lstar routine
        expected = {'Xj': array([[ 0.001051], [ 0.002722]]),
            'Lstar': array([[3.02419 ], [2.053277]]),
            'Blocal': array([ 1019.052401,  3467.52999]),
            'Lm': array([[ 3.091352], [ 2.056261]]),
            'Bmin': array([ 1018.669701,  3459.500966 ]),
            'MLT': array([ 11.97159175,  12.13313906])}
        actual = ib.get_Lstar(self.ticks, self.loci, [90], extMag="OPQUIET", omnivals=self.omnivals,
                              landi2lstar=True)
        for key in expected.keys():
            numpy.testing.assert_almost_equal(expected[key], actual[key], decimal=6)

    def test_AlphaOfK(self):
        '''test calculation of eq. pitch angle from K (regression)'''
        t = spacepy.time.Ticktock(['2001-09-01T04:00:00'], 'ISO')
        loci = spacepy.coordinates.Coords([-4,0,0], 'GSM', 'car', use_irbem=True)
        ans = spacepy.irbempy.AlphaOfK(t, loci, 0.11, extMag='T89', omnivals=self.omnivals)
        numpy.testing.assert_almost_equal(ans, 50.625, decimal=5)

    def test_AlphaOfK_badval(self):
        """test AlphaOfK hitting/handling badval"""
        loci_noncredible = spacepy.coordinates.Coords([[-1e4, 1e4, 0], [2, 0, 0]], 'GEO', 'car', use_irbem=True)
        actual = ib.AlphaOfK(self.ticks, loci_noncredible, K=1, omnivals=self.omnivals)
        self.assertTrue(numpy.isnan(actual).all())

    def test_find_footpoint(self):
        '''test computation of field line footpoint location/magnitude (regression)'''
        expected = {'Bfoot': numpy.array([ 47626.93407,  47625.97051])}
        expected['loci'] = spacepy.coordinates.Coords([[ 99.28759,  56.14644, -10.29427],
                                                           [ 99.33375,  56.14603, -10.29737]],
                                                           dtype='GDZ', carsph='sph',
                                                           units=['km', 'deg', 'deg'],
                                                           use_irbem=True)
        y = spacepy.coordinates.Coords([[3,0,0],[3,0,0]], 'GEO', 'car', use_irbem=True)
        ans = spacepy.irbempy.find_footpoint(self.ticks, y, omnivals=self.omnivals)
        numpy.testing.assert_almost_equal(expected['Bfoot'], ans['Bfoot'], decimal=5)
        numpy.testing.assert_almost_equal(expected['loci'].data, ans['loci'].data, decimal=5)

    def test_find_footpoint_bad_hemi(self):
        with self.assertRaises(ValueError):
            ib.find_footpoint(self.ticks, self.loci, hemi='asdf', omnivals=self.omnivals)

    def test_get_Bfield_badval(self):
        """test get_Bfield hitting badval"""
        loci_noncredible = spacepy.coordinates.Coords([[-1e4, 1e4, 0], [2, 0, 0]], 'GEO', 'car', use_irbem=True)
        actual = ib.get_Bfield(self.ticks, loci_noncredible, omnivals=self.omnivals)
        self.assertTrue(np.isnan(actual["Blocal"][0]))
        self.assertTrue(np.isnan(actual["Bvec"][0]).all())

    def test_find_Bmirror_badval(self):
        """test find_Bmirror hitting badval"""
        loci_noncredible = spacepy.coordinates.Coords([[-1e4, 1e4, 0], [2, 0, 0]], 'GEO', 'car', use_irbem=True)
        actual_badloci = ib.find_Bmirror(self.ticks, loci_noncredible, [45], omnivals=self.omnivals)
        # These will need to be changed slightly once find_Bmirror is fixed
        self.assertTrue(np.isnan(actual_badloci["Blocal"][0]))
        self.assertTrue(np.isnan(actual_badloci["Bmirr"][0]))
        self.assertTrue(np.isnan(actual_badloci["loci"].data[0]).all())

        actual_badalpha = ib.find_Bmirror(self.ticks, self.loci, [0], omnivals=self.omnivals)
        self.assertTrue(np.isnan(actual_badalpha['Bmirr']).all())
        self.assertTrue(np.isnan(actual_badalpha['loci'].data).all())

    def test_find_magequator_badval(self):
        """test find_magequator hitting badval"""
        loci_noncredible = spacepy.coordinates.Coords([[-1e4, 1e4, 0], [2, 0, 0]], 'GEO', 'car', use_irbem=True)
        actual = ib.find_magequator(self.ticks, loci_noncredible, omnivals=self.omnivals)
        self.assertTrue(np.isnan(actual["Bmin"][0]))
        self.assertTrue(np.isnan(actual["loci"].data[0]).all())

    def test_get_Lm(self):
        """test get_Lm (regression)"""
        expected = {'Lm': np.array([[3.06568463], [2.05580772]]),
                    'Bmirr': np.array([[2061.90715087], [6903.89340583]]),
                    'Bmin': np.array([1030.45633741, 3444.07701556]),
                    'Xj': np.array([[1.44884221], [0.98442345]]),
                    'MLT': np.array([11.97159175, 12.13313906])}
        actual = ib.get_Lm(self.ticks, self.loci, [45], omnivals=self.omnivals)
        for key, arr in expected.items():
            numpy.testing.assert_allclose(arr, actual[key])

    def test_get_Lm_bad_intMag(self):
        with self.assertRaises(ValueError):
            ib.get_Lm(self.ticks, self.loci, [45], intMag='asdf')

    def test_get_Lm_bad_IGRFset(self):
        with self.assertRaises(ValueError):
            ib.get_Lm(self.ticks, self.loci, [45], IGRFset=-1)


class IRBEMTestsWithoutOMNI(unittest.TestCase):

    def setUp(self):
        self.ticks = spacepy.time.Ticktock(['2002-02-02T12:00:00', '2002-02-02T12:10:00'], 'ISO')
        self.loci = spacepy.coordinates.Coords([[3,0,0],[2,0,0]], 'GEO', 'car', use_irbem=True)

    def test_get_dtype(self):
        sysaxes = 3
        expected = ('GSE', 'car')
        self.assertEqual(expected, ib.get_dtype(sysaxes))

    def test_prep_irbem_sysaxesnone(self):
        """prep_irbem should handle 'car' and 'sph' version of systems identically"""
        locc = spacepy.coordinates.Coords([[3, 0, 0], [2, 0, 0]],
                                          'GSM', 'car', use_irbem=True)
        out1 = ib.prep_irbem(ticks=self.ticks, loci=locc,
                             extMag='0', options=[1, 0, 0, 0, 1])
        pos = spacepy.coordinates.car2sph(locc.data)
        locs = spacepy.coordinates.Coords(pos, 'GSM', 'sph', use_irbem=True)
        out2 = ib.prep_irbem(ticks=self.ticks, loci=locs,
                             extMag='0', options=[1, 0, 0, 0, 1])
        self.assertEqual(out1['sysaxes'], out2['sysaxes'])
        numpy.testing.assert_almost_equal(out1['xin1'], out2['xin1'])
        numpy.testing.assert_almost_equal(out1['xin2'], out2['xin2'])
        numpy.testing.assert_almost_equal(out1['xin3'], out2['xin3'])

    def test_coord_trans(self):
        self.loci.ticks = self.ticks
        expected = array([[ 2.86714166, -0.02178308,  0.88262348],
            [ 1.91462214,  0.06992421,  0.57387514]])
        numpy.testing.assert_almost_equal(expected, ib.coord_trans(self.loci, 'GSM', 'car'))

    def test_coord_trans_swap(self):
        """test coord_trans with invalid sysaxesout requiring a carsph swap"""
        self.loci.ticks = self.ticks
        expected_swap_car = numpy.array([[1.27354630e+04, 0, 7.79822200e-13],
                                         [6.36426300e+03, 0, 3.89698716e-13]])
        actual_swap_car = ib.coord_trans(self.loci, 'GDZ', 'car')
        numpy.testing.assert_allclose(expected_swap_car, actual_swap_car)
        expected_swap_sph = numpy.array([[3.00001811, 17.05237491, 1.50312982],
                                         [2.00001162, 16.33234518, 4.00302456]])
        actual_swap_sph = ib.coord_trans(self.loci, 'GSE', 'sph')
        numpy.testing.assert_allclose(expected_swap_sph, actual_swap_sph)

    def test_GSM_SM_init(self):
        '''test for initialization error in gsm to sm conversion'''
        real8 = ib.real8
        int4 = ib.int4
        cc_got = np.zeros((3,), dtype=np.float64)
        ib.irbemlib.coord_trans1(
            int4(2), int4(4), int4(2002), int4(33), real8(43200),
            np.asarray([1., 2., 4.]).ctypes.data_as(ib.ctypes.POINTER(real8 * 3)),
            cc_got.ctypes.data_as(ib.ctypes.POINTER(ib.real8 * 3))
        )
        expected = np.array([1.9286, 2., 3.6442])
        # NaN will result if init not done in IRBEM, assert_almost_equal will
        # compare NaNs without complaint
        numpy.testing.assert_almost_equal(expected, cc_got, decimal=3)

    def test_get_AEP8(self):
        """test get_AEP8"""
        c = self.loci
        c.ticks = self.ticks
        E = 2.0  # energy in MeV
        expected = 99492.059080021136
        actual = ib.get_AEP8(E, c)
        numpy.testing.assert_almost_equal(expected, actual, decimal=3)

    def test_get_AEP8_max(self):
        """test get_AEP8 with 'MAX' model and 'RANGE' fluxtype"""
        self.loci.ticks = self.ticks
        E = 2.0
        expected = 405349.88833790703
        actual = ib.get_AEP8(E, self.loci, 'max')
        numpy.testing.assert_almost_equal(expected, actual, decimal=5)

    def test_get_AEP8_min_p(self):
        """test get_AEP8 with 'min' model and proton particles"""
        self.loci.ticks = self.ticks
        E = 2.0
        expected = 7733922.56149766
        actual = ib.get_AEP8(E, self.loci, particles='p')
        numpy.testing.assert_almost_equal(expected, actual, decimal=3)

    def test_get_AEP8_max_p(self):
        """test get_AEP8 with 'max' model and proton particles"""
        self.loci.ticks = self.ticks
        E = 2.0
        expected = 7719051.333830692
        actual = ib.get_AEP8(E, self.loci, 'max', particles='p')
        numpy.testing.assert_almost_equal(expected, actual, decimal=3)

    def test_get_AEP8_range(self):
        """test get_AEP8 with 'range' flux type"""
        self.loci.ticks = self.ticks
        E = [2.0, 3.0]
        actual = ib.get_AEP8(E, self.loci, fluxtype='range')
        self.assertTrue(np.isnan(actual))

    def test_get_AEP8_int(self):
        """test get_AEP8 with 'int' flux type"""
        self.loci.ticks = self.ticks
        E = 2.0
        expected = 65490.42994552884
        actual = ib.get_AEP8(E, self.loci, fluxtype='int')
        numpy.testing.assert_almost_equal(expected, actual, decimal=5)

    def test_get_AEP8_BBo_L(self):
        """Test get_AEP8 with optional version of loci"""
        expected = 11.391557407259167
        actual = ib.get_AEP8(1, [10, 10])
        numpy.testing.assert_almost_equal(expected, actual)


class IRBEMShieldoseTests(spacepy_testing.TestPlot):

    maxDiff = None

    def setUp(self):
        super(IRBEMShieldoseTests, self).setUp()
        self.depths_mil = np.logspace(np.log10(4), np.log10(5000), 30)
        self.depths_mm = self.depths_mil * 0.0254
        self.sd_default = ib.Shieldose2()

    def test_setshielding(self):
        """Setting shielding should appropriately update settings
        """
        sdd = self.sd_default
        tunit = 'mm'
        target = np.logspace(0, 3, 50)
        tcopy = target.copy()
        sdd.set_shielding(depths=target, units=tunit)
        target *= 2  # make sure we're not modifying arrays
        curr_dep = np.asarray(sdd.settings['depths'].copy())
        numpy.testing.assert_array_almost_equal(tcopy, curr_dep)
        numpy.testing.assert_string_equal(sdd.settings['depths'].attrs['UNITS'], tunit)

    def test_mil_mm(self):
        """Should get same results for different depth units
        """
        sd1 = self.sd_default
        sd1.set_shielding(depths=self.depths_mil, units='Mil')
        sd1.get_dose()
        sd2 = ib.Shieldose2()
        sd2.set_shielding(depths=self.depths_mm, units='mm')
        sd2.get_dose()
        de1 = np.asarray(sd1.results['dose_electron'])
        de2 = np.asarray(sd2.results['dose_electron'])
        numpy.testing.assert_array_almost_equal(de1, de2)

    def test_shieldose2_changed(self):
        """Results should be removed if settings are changed
        """
        self.assertFalse(self.sd_default.results)
        self.sd_default.get_dose()
        self.assertTrue(self.sd_default.results)
        self.sd_default.set_shielding(depths=self.depths_mm, units='mm')
        self.assertFalse(self.sd_default.results)

    def test_invalid_det(self):
        """Asking for invalid detector material raises ValueError
        """
        self.assertRaises(ValueError, self.sd_default.get_dose, detector=99)

    def test_invalid_fluence(self):
        """Asking for invalid fluence model issues UserWarning
        """
        self.assertWarns(UserWarning,
                         self.sd_default.get_dose,
                         fluence='notamodel')

    def test_e_j_mismatch(self):
        """Mismatched flux energy array sizes raises ValueError
        """
        jarr = np.logspace(0, 4, 35)[::-1]
        earr = np.logspace(1, 10, 40)
        self.assertRaises(ValueError, self.sd_default.set_flux,
                          jarr, earr, 'e')

    def test_plot_e(self):
        """Check for expected outputs in electron dose plot"""
        self.sd_default.get_dose()
        res = self.sd_default.results
        f1, a1, l1 = self.sd_default.plot_dose(source=['e'])
        f2, a2, l2 = self.sd_default.plot_dose(source=['e', 'brems'])
        self.assertEqual(3, len(l1))
        self.assertEqual(3, len(l2))
        np.testing.assert_array_equal(l1[0][0].get_xdata(),
                                      res['depths'])
        np.testing.assert_array_equal(l1[0][0].get_ydata(),
                                      res['dose_electron'][:, 0])
        np.testing.assert_array_equal(l2[0][0].get_ydata(),
                                      res['dose_electron'][:, 0] +
                                      res['dose_bremsstrahlung'][:, 0])
        self.assertEqual('Dose [Silicon]', a1.get_ylabel())
        self.assertEqual('Depth [Mil]', a1.get_xlabel())

    def test_plot_p_noleg(self):
        """Check for expected outputs in proton dose plot"""
        self.sd_default.get_dose()
        res = self.sd_default.results
        f1, a1, l1 = self.sd_default.plot_dose(source=['p_tr'],
                                               add_legend=False)
        self.assertEqual(3, len(l1))
        np.testing.assert_array_equal(l1[0][0].get_xdata(),
                                      res['depths'])
        np.testing.assert_array_equal(l1[0][0].get_ydata(),
                                      res['dose_proton_trapped'][:, 0])
        self.assertEqual('Dose [Silicon]', a1.get_ylabel())
        self.assertEqual('Depth [Mil]', a1.get_xlabel())
        self.assertIs(None, a1.get_legend())

    def test_plot_brems(self):
        """Check for expected outputs in bremsstrahlung-only dose plot"""
        self.sd_default.get_dose()
        res = self.sd_default.results
        f, a, l = self.sd_default.plot_dose(source=['brems'])
        self.assertEqual(3, len(l))
        np.testing.assert_array_equal(l[0][0].get_xdata(),
                                      res['depths'])
        np.testing.assert_array_equal(l[0][0].get_ydata(),
                                      res['dose_bremsstrahlung'][:, 0])
        self.assertEqual('Dose [Silicon]', a.get_ylabel())
        self.assertEqual('Depth [Mil]', a.get_xlabel())

    def test_plot_p_un(self):
        """Check for expected outputs in untrapped proton dose plot"""
        self.sd_default.get_dose()
        res = self.sd_default.results
        f, a, l = self.sd_default.plot_dose(source=['p_un'])
        self.assertEqual(3, len(l))
        np.testing.assert_array_equal(l[0][0].get_xdata(),
                                      res['depths'])
        np.testing.assert_array_equal(l[0][0].get_ydata(),
                                      res['dose_proton_untrapped'][:, 0])
        leg = a.get_legend()
        self.assertEqual(
            [f"Protons (untrapped)\n{g}" for g in
             ['Semi-Inf Slab', 'Finite Slab', 'Spherical']],
            [t.get_text() for t in leg.texts])

    def test_plot_tot(self):
        """Check for expected outputs in total dose plot"""
        self.sd_default.get_dose()
        res = self.sd_default.results
        f, a, l = self.sd_default.plot_dose(source=['tot'])
        self.assertEqual(3, len(l))
        np.testing.assert_array_equal(l[0][0].get_xdata(),
                                      res['depths'])
        np.testing.assert_array_equal(l[0][0].get_ydata(),
                                      res['dose_total'][:, 0])

    def test_regression_si(self):
        """Check for expected numerical result"""
        expect_tot_500 = np.array([2.174920520699405e-15,
                                   1.7185079165053166e-15,
                                   4.750370701125187e-15])
        self.sd_default.set_shielding(depths=[100, 500, 1000], units='Mil')
        self.sd_default.get_dose(detector=3)
        dtot = np.asarray(self.sd_default.results['dose_total'])
        np.testing.assert_array_almost_equal(dtot[1, :], expect_tot_500,
                                             decimal=15)

    def test_str(self):
        """Check string representation"""
        self.sd_default.set_shielding(depths=self.depths_mil, units='Mil')
        res = str(self.sd_default)
        expected = """spacepy.irbempy.Shieldose2
|____settings
     |____calc_flag (bool)
     |____depths (spacepy.datamodel.dmarray (30,))
         :|____UNITS (str [3])
     |____depthunit (int)
     |____energy_e (numpy.ndarray (30,))
     |____energy_p_tr (numpy.ndarray (299,))
     |____energy_p_un (numpy.ndarray (299,))
     |____flux_e (numpy.ndarray (30,))
     |____flux_p_tr (numpy.ndarray (299,))
     |____flux_p_un (numpy.ndarray (299,))
     |____tau (int)
     |____unit_en (int)
"""
        self.assertEqual(expected, res)
        self.sd_default.get_dose()
        res = str(self.sd_default)
        expected = """spacepy.irbempy.Shieldose2
|____settings
     |____calc_flag (bool)
     |____depths (spacepy.datamodel.dmarray (30,))
         :|____UNITS (str [3])
     |____depthunit (int)
     |____detector (int)
     |____detector_material (str [7])
     |____emaxe (numpy.float64 ())
     |____emaxptr (numpy.float64 ())
     |____emaxpun (numpy.float64 ())
     |____emine (numpy.float64 ())
     |____eminptr (numpy.float64 ())
     |____eminpun (numpy.float64 ())
     |____energy_e (numpy.ndarray (30,))
     |____energy_p_tr (numpy.ndarray (299,))
     |____energy_p_un (numpy.ndarray (299,))
     |____flux_e (numpy.ndarray (30,))
     |____flux_p_tr (numpy.ndarray (299,))
     |____flux_p_un (numpy.ndarray (299,))
     |____jemax (int)
     |____jpmax (int)
     |____jsmax (int)
     |____len_e (int)
     |____len_p (int)
     |____ndepth (int)
     |____nucmeth (int)
     |____tau (int)
     |____unit_en (int)
|____results
     |____depths (spacepy.datamodel.dmarray (30,))
     |____dose_bremsstrahlung (spacepy.datamodel.dmarray (30, 3))
     |____dose_electron (spacepy.datamodel.dmarray (30, 3))
     |____dose_proton_trapped (spacepy.datamodel.dmarray (30, 3))
     |____dose_proton_untrapped (spacepy.datamodel.dmarray (30, 3))
     |____dose_total (spacepy.datamodel.dmarray (30, 3))
     |____fluence_electron (spacepy.datamodel.dmarray (30, 3))
         :|____NOTES (str [48])
"""
        self.assertEqual(expected, res)

    def test_repr(self):
        """Check representation"""
        self.sd_default.set_shielding(depths=self.depths_mil, units='Mil')
        res = repr(self.sd_default)
        expected = "<Shieldose2(Depths = 30; Dose not calculated)>"
        self.assertEqual(expected, res)
        self.sd_default.get_dose()
        res = repr(self.sd_default)
        expected = "<Shieldose2(Depths = 30; Dose calculated)>"
        self.assertEqual(expected, res)

    def test_bad_units(self):
        """Pass invalid units"""
        with self.assertRaises(ValueError) as cm:
            self.sd_default.set_shielding(depths=self.depths_mil, units='junk')
        expected = "Units must be one of mil, g/cm2, mm, not junk"
        self.assertEqual(expected, str(cm.exception))

    def test_reset_flux(self):
        """Check representation"""
        self.sd_default.set_shielding(depths=self.depths_mil, units='Mil')
        self.assertFalse(self.sd_default.results)
        self.assertFalse(self.sd_default.settings['calc_flag'])
        self.sd_default.get_dose()
        self.assertTrue(self.sd_default.results)
        self.assertTrue(self.sd_default.settings['calc_flag'])
        en_e = np.arange(10)
        # Nonsense, but it's different nonsense
        self.sd_default.set_flux(en_e ** 2, en_e, 'e')
        self.assertFalse(self.sd_default.results)
        self.assertFalse(self.sd_default.settings['calc_flag'])


# -----------------------------------------------------------------------


if __name__ == "__main__":
    # suite	=	unittest.TestLoader().loadTestsFromTestCase(SimpleFunctionTests)
    # unittest.TextTestRunner(verbosity=2).run(suite)

    # suite	=	unittest.TestLoader().loadTestsFromTestCase(tFunctionTests)
    # unittest.TextTestRunner(verbosity=2).run(suite)

    unittest.main()
