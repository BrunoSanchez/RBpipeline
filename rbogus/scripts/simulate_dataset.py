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
import time
#import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits
from astropy.io import ascii
from astropy.table import Table
import pandas as pd
import sep

import ois
from properimage import single_image as si
from properimage import propersubtract as ps
from properimage import utils

from . import stuffskywrapper as w

from corral.conf import settings

def main(params):
    t0 = time.time()
    imgs_dir = params['path']
    conf_dir = os.path.join(imgs_dir, "conf")
    if not os.path.isdir(conf_dir):
        os.makedirs(conf_dir)
    cats_dir = os.path.join(imgs_dir, "cats")
    if not os.path.isdir(cats_dir):
        os.makedirs(cats_dir)
#def main(imgs_dir, sim_cube={}):
    # refstarcount_zp, refstarcount_slope, refseeing_fwhm):

    if not os.path.isdir(imgs_dir):
        os.makedirs(imgs_dir)

    # generate stuff cat
    stuffconf = {'cat_name' : os.path.join(cats_dir, 'gxcat.list'),
                 'im_w'     : 1024,
                 'im_h'     : 1024,
                 'px_scale' : params['px_scale'],
                 'eff_col'  : params['eff_col']
                 }

    w.write_stuffconf(os.path.join(conf_dir, 'conf.stuff'),
                      stuffconf)
    cat_name = stuffconf['cat_name']
    w.run_stuff(os.path.join(conf_dir, 'conf.stuff'))

    # generate the Reference image
    skyconf = {'image_name' : 'test.fits',
               'image_size' : 1024,
               'exp_time'   : params['exp_time'],
               'mag_zp'     : 25.,
               'px_scale'   : params['px_scale'],
               'seeing_fwhm': params['ref_fwhm'],
               'starcount_zp': params['ref_starzp'],
               'starcount_slope': params['ref_starslope'],
               'm1_diam'    : params['m1_diam'],
               'm2_diam'    : params['m2_diam'],
               'back_sbright' : params['ref_back_sbright']
               }

    w.write_skyconf(os.path.join(conf_dir, 'conf.sky'), skyconf)
    ref = w.run_sky(os.path.join(conf_dir, 'conf.sky'), cat_name,
                    img_path=os.path.join(imgs_dir, 'ref.fits'))

    # add some transients over the galaxies
    rows = []
    #objcat = open(os.path.join(imgs_dir, 'ref.list'))
    cols = ['code', 'x', 'y', 'mag', 'bulge_total',
            'bulge_eff_r', 'bulge_app_aspect',
            'bulge_PA', 'disk_scale_len',
            'disk_app_aspect', 'disk_PA',
            'z', 'hubble_type']
    objcat = pd.read_table(os.path.join(imgs_dir, 'ref.list'), names=cols,
                           sep='\s+', index_col=False)
    gx_to_z1 = (objcat.code==200) & (objcat.z <1.)

    for arow in objcat[gx_to_z1].itertuples(index=False):
        if np.random.random() > 0.80:

            disk_scale_len_px = arow.disk_scale_len/skyconf['px_scale']

            dist_scale_units = np.random.random() * 5.
            #delta_pos = np.random.random()*2. - 1.
            angle = np.random.random()*2*np.pi

            x = arow.x + dist_scale_units * disk_scale_len_px * np.cos(angle)
            y = arow.y + dist_scale_units * disk_scale_len_px * np.sin(angle)

            #x = row[1] + delta_pos * dist_scale_units * disk_scale_len_px
            #y = row[2] + np.sqrt(1.-delta_pos*delta_pos)*dist_scale_units * disk_scale_len_px

            app_mag = 5. * (np.random.random()-0.8) + arow.mag
            if x>1014. or y>1014. or x<10. or y<10.:
                continue
            else:
                newrow = [100, x, y, app_mag, dist_scale_units, angle]
                rows.append(newrow + list(arow))

    newcat_cols = ['code', 'x', 'y', 'app_mag', 'r_scales', 'PA_angle']
    newcat_cols = newcat_cols + ['gx_'+nam for nam in cols]
    newcat = Table(rows=rows, names=newcat_cols)
    cat_cols = ['code', 'x', 'y', 'app_mag']
    newcat[cat_cols].write(os.path.join(cats_dir, 'transient.list'),
                           format='ascii.fast_no_header',
                           overwrite=True)

    os.system('cat '+os.path.join(imgs_dir, 'ref.list')+' >> '+
               os.path.join(cats_dir, 'transient.list'))

    # generate the new image
    skyconf = {'image_name' : 'test.fits',
               'image_size' : 1024,
               'exp_time'   : params['exp_time'],
               'mag_zp'     : 25.0,
               'px_scale'   : params['px_scale'],
               'seeing_fwhm': params['new_fwhm'],
               'starcount_zp': 3e-4,
               'starcount_slope': 0.2,
               'm1_diam'    : params['m1_diam'],
               'm2_diam'    : params['m2_diam'],
               'back_sbright' : params['new_back_sbright']
               }

    cat_name = os.path.join(cats_dir, 'transient.list')
    w.write_skyconf(os.path.join(conf_dir, 'conf.sky'), skyconf)

    new = w.run_sky(os.path.join(conf_dir, 'conf.sky'), cat_name,
                    img_path=os.path.join(imgs_dir, 'new.fits'))
    tf = time.time()
    print('Took {} time to generate sky fits'.format(t0-tf))
    print('Images to be subtracted: {} {}'.format(ref, new))

##  With properimage
    #with ps.ImageSubtractor(ref, new, align=False, solve_beta=False) as sub:
    #    D, P, S = sub.subtract()
    print('Starting properimage')
    t0 = time.time()
    try:
        D, P, S, mask = ps.diff(str(ref), str(new), align=False, beta=False,
                                iterative=False, shift=False)
    except ValueError:
        raise
    dt_z = time.time() - t0
    #import ipdb; ipdb.set_trace()
    utils.encapsule_R(D, path=os.path.join(imgs_dir, 'diff.fits'))
    utils.encapsule_R(P, path=os.path.join(imgs_dir, 'psf_d.fits'))
    utils.encapsule_R(S, path=os.path.join(imgs_dir, 's_diff.fits'))
    print('Finish storing properimage. Took {} time'.format(dt_z))

    # import ipdb; ipdb.set_trace()
    scorrdetected = utils.find_S_local_maxima(S, threshold=3.5)
    print('S_corr found thath {} transients were above 3.5 sigmas'.format(len(scorrdetected)))
    ascii.write(table=np.asarray(scorrdetected),
                output=os.path.join(imgs_dir, 's_corr_detected.csv'),
                names=['X_IMAGE', 'Y_IMAGE', 'SIGNIFICANCE'],
                #format='csv',
                overwrite=True)

    S = np.ascontiguousarray(S)
    #~ s_bkg = sep.Background(S)
    from astropy.stats import sigma_clipped_stats
    mean, median, std = sigma_clipped_stats(S)
    sdetected = sep.extract(S-median, 3.5*std,
                            filter_kernel=None)
    print('S_corr with sep found thath {} transients were above 3.5 sigmas'.format(len(sdetected)))
    ascii.write(table=sdetected,
                output=os.path.join(imgs_dir, 'sdetected.csv'),
                #format='csv',
                overwrite=True)

##  With OIS
    print('Starting OIS')
    t0 = time.time()
    n = fits.getdata(new)
    r = fits.getdata(ref)
    #import statprof
    #statprof.start()
    #try:
    ois_d = ois.optimal_system(n, r, method='Bramich')[0]
    #finally:
        #statprof.stop()
        #statprof.display(open('output_statprof.txt', 'w'))
    del(n)
    del(r)
    dt_o = time.time() - t0
    utils.encapsule_R(ois_d, path=os.path.join(imgs_dir, 'diff_ois.fits'))
    print('Finish storing OIS. Took {} time'.format(dt_o))

##  With HOTPANTS
    print('Starting hotpants')
    t0 = time.time()
    os.system('hotpants -v 0 -inim {} -tmplim {} -outim {} -tu 400000 -iu 40000'.format(new, ref,
        os.path.join(imgs_dir, 'diff_hot.fits')))
    dt_h = time.time() - t0
    print('Finish hotpants. Took {} time'.format(dt_h))

    return [newcat.to_pandas(), [dt_z, dt_o, dt_h]]


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
