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
from . import simulate_dataset as sd
from . import stuffskywrapper as w

from corral.conf import settings

import pickle

def main(params):
#def main(index=0, sim_cube={}):
    # zp=6e4, slope=0.3, ref_fwhm=0.9):
    #suffix = 'img{}'.format(str(index).zfill(5))
    #curr_dir = os.path.join(settings.IMGS_PATH, suffix)
    curr_dir = params['path']

    conf_dir = os.path.join(curr_dir, "conf")
    if not os.path.isdir(conf_dir):
        os.makedirs(conf_dir)
    cats_dir = os.path.join(curr_dir, "cats")
    if not os.path.isdir(cats_dir):
        os.makedirs(cats_dir)
    #~ results_dir = os.path.join(curr_dir, "results")
    #~ if not os.path.isdir(results_dir):
        #~ os.makedirs(results_dir)



    #Generation happens here
    try:
        transients, times = sd.main(params)
        print('succesful generation')
    except:
        return('error101')

    #import ipdb; ipdb.set_trace()
    #zp, slope, ref_fwhm)
    #
    diff_path = os.path.join(curr_dir, 'diff.fits')
    cat_out = os.path.join(cats_dir, 'outcat.dat')

    w.run_sex(os.path.join(curr_dir, '../../config/conf.sex'),
              diff_path, cat_output=cat_out)
    #
    diff_ois_path = os.path.join(curr_dir, 'diff_ois.fits')
    cat_ois_out = os.path.join(cats_dir, 'outcat_ois.dat')

    w.run_sex(os.path.join(curr_dir, '../../config/conf.sex'),
              diff_ois_path, cat_output=cat_ois_out)
    #
    diff_hot_path = os.path.join(curr_dir, 'diff_hot.fits')
    cat_hot_out = os.path.join(cats_dir, 'outcat_hot.dat')

    w.run_sex(os.path.join(curr_dir, '../../config/conf.sex'),
              diff_hot_path, cat_output=cat_hot_out)

# =============================================================================
# SCorr Detections
# =============================================================================
    scorrdetections = ascii.read(os.path.join(curr_dir, 's_corr_detected.csv')).to_pandas()
    #scorrdetections['id'] = np.repeat(None, len(scorrdetections))

# =============================================================================
# S Detections
# =============================================================================
    sdetections = ascii.read(os.path.join(curr_dir, 'sdetected.csv')).to_pandas()

    deltax = list(sdetections["xmax"] - sdetections["xmin"])
    deltay = list(sdetections["ymax"] - sdetections["ymin"])
    ratio = [float(min(dx,dy))/float(max(dx,dy,1))
             for dx, dy in zip(deltax, deltay)]

    roundness = list(sdetections["a"] / sdetections["b"])

    pk_cent = list(np.sqrt((sdetections['xcpeak']-sdetections['x'])**2
                     + (sdetections['ycpeak'] - sdetections['y'])**2))

    sdetections['DELTAX'] = deltax
    sdetections['DELTAY'] = deltay
    sdetections['RATIO'] = ratio
    sdetections['ROUNDNESS'] = roundness
    sdetections['PEAK_CENTROID'] = pk_cent
    #sdetections['id'] = np.repeat(None, len(deltax))

# =============================================================================
#  PS detections
# =============================================================================
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
    #detections['id'] = np.repeat(None, len(deltax))

# =============================================================================
#   OIS detections
# =============================================================================
    detections_ois = ascii.read(cat_ois_out, format='sextractor').to_pandas()

    deltax = list(detections_ois["XMAX_IMAGE"] - detections_ois["XMIN_IMAGE"])
    deltay = list(detections_ois["YMAX_IMAGE"] - detections_ois["YMIN_IMAGE"])
    ratio = [float(min(dx,dy))/float(max(dx,dy,1))
             for dx, dy in zip(deltax, deltay)]

    roundness = list(detections_ois["A_IMAGE"] / detections_ois["B_IMAGE"])

    pk_cent = list(np.sqrt((detections_ois['XPEAK_IMAGE']-detections_ois['X_IMAGE'])**2
                     + (detections_ois['YPEAK_IMAGE'] - detections_ois['Y_IMAGE'])**2))

    detections_ois['DELTAX'] = deltax
    detections_ois['DELTAY'] = deltay
    detections_ois['RATIO'] = ratio
    detections_ois['ROUNDNESS'] = roundness
    detections_ois['PEAK_CENTROID'] = pk_cent
    #detections_ois['id'] = np.repeat(None, len(deltax))

# =============================================================================
#   HOT detections
# =============================================================================
    detections_hot = ascii.read(cat_hot_out, format='sextractor').to_pandas()

    deltax = list(detections_hot["XMAX_IMAGE"] - detections_hot["XMIN_IMAGE"])
    deltay = list(detections_hot["YMAX_IMAGE"] - detections_hot["YMIN_IMAGE"])
    ratio = [float(min(dx,dy))/float(max(dx,dy,1))
             for dx, dy in zip(deltax, deltay)]

    roundness = list(detections_hot["A_IMAGE"] / detections_hot["B_IMAGE"])

    pk_cent = list(np.sqrt((detections_hot['XPEAK_IMAGE']-detections_hot['X_IMAGE'])**2
                     + (detections_hot['YPEAK_IMAGE'] - detections_hot['Y_IMAGE'])**2))

    detections_hot['DELTAX'] = deltax
    detections_hot['DELTAY'] = deltay
    detections_hot['RATIO'] = ratio
    detections_hot['ROUNDNESS'] = roundness
    detections_hot['PEAK_CENTROID'] = pk_cent
    #detections_hot['id'] = np.repeat(None, len(deltax))


    #~ detections.to_pickle(os.path.join(results_dir, 'detections.pkl'),
    #~ protocol=2)
    #~ detections_ois.to_pickle(os.path.join(results_dir, 'detections_ois.pkl'),
    #~ protocol=2)
    #~ detections_hot.to_pickle(os.path.join(results_dir, 'detections_hot.pkl'),
    #~ protocol=2)
    #~ transients.to_pickle(os.path.join(results_dir, 'transients.pkl'),
    #~ protocol=2)
    #~ sdetections.to_pickle(os.path.join(results_dir, 'sdetections.pkl'),
    #~ protocol=2)
    #~ scorrdetections.to_pickle(os.path.join(results_dir,
    #~ 'scorrdetections.pkl'), protocol=2)
    #~ with open(os.path.join(results_dir, 'times.pkl'), 'w') as fp:
        #~ pickle.dump(times, fp, protocol=2)
    results = []

    results.append(diff_path)
    results.append(detections)
    results.append(diff_ois_path)
    results.append(detections_ois)
    results.append(diff_hot_path)
    results.append(detections_hot)
    results.append(transients)
    results.append(sdetections)
    results.append(scorrdetections)
    results.append(times)

    return results

