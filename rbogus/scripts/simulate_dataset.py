#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  simulate_dataset.py
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
import shutil
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.io import ascii
from astropy.table import Table

import ois
from properimage import propercoadd as pc
from properimage import propersubtract as ps
from properimage import utils

import stuffskywrapper as w

from corral.conf import settings

def main(imgs_dir):

    if not os.path.isdir(imgs_dir):
        os.makedirs(imgs_dir)

    # generate stuff cat
    stuffconf = {'cat_name' : os.path.join(settings.CATS_PATH, 'gxcat.list'),
                 'im_w'     : 1024,
                 'im_h'     : 1024,
                 'px_scale' : 0.3
                 }

    w.write_stuffconf(os.path.join(settings.CONFIG_PATH, 'conf.stuff'),
                      stuffconf)
    cat_name = stuffconf['cat_name']
    w.run_stuff(os.path.join(settings.CONFIG_PATH, 'conf.stuff'))

    # generate the Reference image
    skyconf = {'image_name' : 'test.fits',
               'image_size' : 1024,
               'exp_time'   : 300,
               'mag_zp'     : 25.0,
               'px_scale'   : 0.3,
               'seeing_fwhm': 0.90,
               'starcount_zp': 6e4,
               'starcount_slope': 0.3
               }

    w.write_skyconf(os.path.join(settings.CONFIG_PATH, 'conf.sky'), skyconf)
    ref = w.run_sky(os.path.join(settings.CONFIG_PATH, 'conf.sky'), cat_name,
                    img_path=os.path.join(imgs_dir, 'ref.fits'))

    # add some transients over the galaxies
    rows = []
    objcat = open(os.path.join(imgs_dir, 'ref.list'))
    for aline in objcat.readlines():
        row = aline.split()
        if row[0] == '200':
            if np.random.random() > 0.80:
                row = np.array(row, dtype=float)
                disk_scale_len_px = row[8]/skyconf['px_scale']

                dist_scale_units = np.random.random() * 5.* disk_scale_len_px
                delta_pos = np.random.random()

                x = row[1] + delta_pos * dist_scale_units
                y = row[2] + np.sqrt(1-delta_pos*delta_pos)*dist_scale_units

                app_mag = 4. * (np.random.random()-0.5) + row[3]
                rows.append([100, x, y, app_mag,
                             delta_pos*dist_scale_units, row[3]])

    #~ rows = []
    #~ for i in xrange(40):
        #~ code = 100
        #~ x = np.random.randint(20, 1004)
        #~ y = np.random.randint(20, 1004)
        #~ app_mag = 4. * np.random.random() + 19.
        #~ row = [code, x, y, app_mag]
        #~ #row.extend(np.zeros(9))
        #~ rows.append(row)

    newcat = Table(rows=rows, names=['code', 'x', 'y', 'app_mag',
                                     'r_scales', 'gx_mag'])
    cat_cols = ['code', 'x', 'y', 'app_mag']
    newcat[cat_cols].write(os.path.join(settings.CATS_PATH, 'transient.list'),
                           format='ascii.fast_no_header')

    os.system('cat '+os.path.join(imgs_dir, 'ref.list')+' >> '+
               os.path.join(settings.CATS_PATH, 'transient.list'))

    # generate the new image
    skyconf = {'image_name' : 'test.fits',
               'image_size' : 1024,
               'exp_time'   : 300,
               'mag_zp'     : 25.0,
               'px_scale'   : 0.3,
               'seeing_fwhm': 0.95,
               'starcount_zp': 3e-4,
               'starcount_slope': 0.2
               }

    cat_name = os.path.join(settings.CATS_PATH, 'transient.list')
    w.write_skyconf(os.path.join(settings.CONFIG_PATH, 'conf.sky'), skyconf)

    new = w.run_sky(os.path.join(settings.CONFIG_PATH, 'conf.sky'), cat_name,
                    img_path=os.path.join(imgs_dir, 'new.fits'))

    print 'Images to be subtracted: {} {}'.format(ref, new)

##  With properimage
    with ps.ImageSubtractor(ref, new, align=False) as subtractor:
        D, P = subtractor.subtract()

    xc, yc = np.where(P.real==np.max(P.real))
    #print xc, yc
    P = P.real[0:2*np.int(xc), 0:2*np.int(yc)]

    d_shifted = np.ones(D.shape) * np.median(D)
    d_shifted[:-int(xc)/2, :-int(yc)/2] = D[int(xc)/2:, int(yc)/2:]

    #utils.encapsule_R(d_shifted,
    #                  path=os.path.join(imgs_dir, 'shifted_diff.fits'))
    #D = d_shifted

    utils.encapsule_R(d_shifted, path=os.path.join(imgs_dir, 'diff.fits'))
    utils.encapsule_R(P, path=os.path.join(imgs_dir, 'psf_d.fits'))

##  With OIS
    ois_d = ois.optimal_system(fits.getdata(new), fits.getdata(ref))[0]
    utils.encapsule_R(ois_d, path=os.path.join(imgs_dir, 'diff_ois.fits'))

##  With HOTPANTS
    os.system('hotpants -inim {} -tmplim {} -outim {}'.format(new, ref,
        os.path.join(imgs_dir, 'diff_hot.fits')))

    return newcat.to_pandas()


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
