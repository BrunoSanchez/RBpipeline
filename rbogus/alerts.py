#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at 2016-12-14T10:42:52.224316 by corral 0.0.1


# =============================================================================
# DOCS
# =============================================================================

"""rbogus alerts

"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import run
from corral.run import endpoints as ep

from . import models

import matplotlib.pyplot as plt



# =============================================================================
# ALERTS
# =============================================================================

#~ class LogScatter(ep.EndPoint):

    #~ def __init__(self, path, xfield, yfield, title, **kwargs):
        #~ self.path = path
        #~ self.xfield = xfield
        #~ self.yfield = yfield
        #~ self.title = title
        #~ self.kwargs = kwargs
        #~ self._x, self._y = [], []

    #~ def process(self, hz):
        #~ planet = hz.planet
        #~ x, y = getattr(planet, self.xfield), getattr(planet, self.yfield)
        #~ if x and y:
            #~ self._x.append(x)
            #~ self._y.append(y)

    #~ def teardown(self, *args):
        #~ plt.scatter(np.log(self._x), np.log(self._y), **self.kwargs)
        #~ plt.title(self.title)
        #~ plt.legend(loc="best")
        #~ plt.savefig(self.path)
        #~ super(LogScatter, self).teardown(*args)


#~ class Histogram(ep.EndPoint):

    #~ def __init__(self, path, xfield, title, **kwargs):
        #~ self.path = path
        #~ self.xfield = xfield
        #~ self.title = title
        #~ self.kwargs = kwargs
        #~ self._x, self._y = [], []

    #~ def process(self, row):
        #~ planet = hz.planet
        #~ x, y = getattr(planet, self.xfield), getattr(planet, self.yfield)
        #~ if x and y:
            #~ self._x.append(x)
            #~ self._y.append(y)




#~ class SimulatedHist(run.Alert):

    #~ model = models.Simulated
    #~ conditions = []  # noqa
    #~ alert_to = [
        #~ Histogram("simulated_mag_hist.png", xfield="mag",
                   #~ title="Injected sources lum fun")]

    #~ def generate(self):


    #~ def render_alert(self, simu):
