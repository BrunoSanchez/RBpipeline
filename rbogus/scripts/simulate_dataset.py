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
import sep

import ois
from properimage import propercoadd as pc
from properimage import propersubtract as ps
from properimage import utils

import stuffskywrapper as w

from corral.conf import settings

def main(imgs_dir, refstarcount_zp, refstarcount_slope, refseeing_fwhm):

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
               'seeing_fwhm': refseeing_fwhm,
               'starcount_zp': refstarcount_zp,
               'starcount_slope': refstarcount_slope
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
                delta_pos = np.random.random()*2. - 1.

                x = row[1] + delta_pos * dist_scale_units
                y = row[2] + np.sqrt(1.-delta_pos*delta_pos)*dist_scale_units

                app_mag = 4. * (np.random.random()-0.5) + row[3]
                if x>1014. or y>1014. or x<10. or y<10.:
                    continue
                else:
                    rows.append([100, x, y, app_mag,
                                 np.abs(delta_pos)*dist_scale_units, row[3]])

    newcat = Table(rows=rows, names=['code', 'x', 'y', 'app_mag',
                                     'r_scales', 'gx_mag'])
    cat_cols = ['code', 'x', 'y', 'app_mag']
    newcat[cat_cols].write(os.path.join(settings.CATS_PATH, 'transient.list'),
                           format='ascii.fast_no_header',
                           overwrite=True)

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
    with ps.ImageSubtractor(ref, new, align=False, solve_beta=False) as sub:
        D, P, S = sub.subtract()

    utils.encapsule_R(D, path=os.path.join(imgs_dir, 'diff.fits'))
    utils.encapsule_R(P, path=os.path.join(imgs_dir, 'psf_d.fits'))
    utils.encapsule_R(S, path=os.path.join(imgs_dir, 's_diff.fits'))

    sdetected = utils.find_S_local_maxima(S, threshold=2.5)
    ascii.write(table=np.asarray(sdetected),
                output=os.path.join(imgs_dir, 's_corr_detected.csv'),
                names=['X_IMAGE', 'Y_IMAGE', 'SIGNIFICANCE'],
                format='csv')

    S = np.ascontiguousarray(S)
    #~ s_bkg = sep.Background(S)
    sdetected = sep.extract(S, 2.5*np.std(S),
                            filter_kernel=None)
    ascii.write(table=sdetected,
                output=os.path.join(imgs_dir, 'sdetected.csv'),
                format='csv')

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
