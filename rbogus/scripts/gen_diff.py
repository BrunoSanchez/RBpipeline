#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  run_fullexperiment.py
#
#  Copyright 2016 Bruno S <bruno@oac.unc.edu.ar>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import os
import numpy as np
from astropy.io import ascii
import simulate_dataset as sd
import stuffskywrapper as w

from corral.conf import settings

def main(index=0):
    suffix = 'img{}'.format(str(index).zfill(5))

    curr_dir = os.path.join(settings.IMGS_PATH, suffix)

    transients = sd.main(curr_dir)

    diff_path = os.path.join(curr_dir, 'diff.fits')
    cat_out = os.path.join(settings.CATS_PATH,'outcat.dat')

    w.run_sex(os.path.join(settings.CONFIG_PATH, 'conf.sex'),
              diff_path, cat_output=cat_out)

    detections = ascii.read(cat_out, format='sextractor').to_pandas()

    deltax = list(detections["XMAX_IMAGE"] - detections["XMIN_IMAGE"])
    deltay = list(detections["YMAX_IMAGE"] - detections["YMIN_IMAGE"])
    ratio = [float(min(dx,dy))/float(max(dx,dy,1))
             for dx, dy in zip(deltax, deltay)]

    roundness = list(detections["A_IMAGE"] / detections["B_IMAGE"])

    pk_cent = list(np.sqrt((detections['XPEAK_IMAGE']-detections['X_IMAGE'])**2
                     + (detections['YPEAK_IMAGE'] - detections['Y_IMAGE'])**2))

    detections['DELTAX'] = deltax
    detections['DELTAY'] = deltay
    detections['RATIO'] = ratio
    detections['ROUNDNESS'] = roundness
    detections['PEAK_CENTROID'] = pk_cent

    #detections['IMAGE'] = np.repeat(diff_path, len(deltax))
    detections['id'] = np.repeat(None, len(deltax))
    detections['CROSSMATCHED'] = np.repeat(False, len(deltax))

    return diff_path, detections






