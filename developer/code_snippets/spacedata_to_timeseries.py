#!/usr/bin/env python

"""Convert a SpaceData object to sunpy TimeSeries"""

import astropy.units
import numpy
import pandas
import spacepy
import spacepy.pycdf
import spacepy.pycdf.istp
import sunpy.timeseries


# data from http://research.ssl.berkeley.edu/data/psp/data/sci/fields/l2/mag_SC_1min/2020/08/psp_fld_l2_mag_SC_1min_20200801_v02.cdf
with spacepy.pycdf.CDF('./psp_fld_l2_mag_SC_1min_20200801_v02.cdf') as f:
    b = spacepy.pycdf.istp.VarBundle(f['psp_fld_l2_mag_SC_1min'])
    sd = b.toSpaceData()

# Convenience, attrs of main var
a = sd['psp_fld_l2_mag_SC_1min'].attrs
# GenericTimeSeries doesn't support ndarray, despite what the docs say
#data = numpy.hstack((sd['epoch_mag_SC_1min'][:, None],
#                     sd['psp_fld_l2_mag_SC_1min']))
data = pandas.DataFrame(
    data=sd['psp_fld_l2_mag_SC_1min'],
    index=sd[a['DEPEND_0']],
    columns=sd[a['LABL_PTR_1']],
    copy=True,  # Editing the data in the ts WILL change the dmarray
)
u = astropy.units.Unit(a['UNITS'], parse_strict='silent')
if isinstance(u, astropy.units.UnrecognizedUnit):
    u = a['UNITS']
ts = sunpy.timeseries.GenericTimeSeries(
    data=data,
    units={l: u for l in data.columns},
)
ts.plot()
