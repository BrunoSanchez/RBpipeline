"""Local settings for rbpipeline"""

IMGS_PATH = '/home/bruno/Data/NewRBpipeline/images'
CONFIG_PATH = '/home/bruno/Data/NewRBpipeline/config'
CATS_PATH = '/home/bruno/Data/NewRBpipeline/cats'

import os
import ujson

if os.path.isfile('sim_cube.pkl'):
    print 'reading cube'
    with open('sim_cube.pkl', 'rb') as fp:
        SIM_CUBE = ujson.load(fp)

else:
    print 'generating cube'
    SIM_CUBE = []

    for ref_starzp in [4e3, 8e3, 16e3, 32e3, 64e3]:
        for ref_starslope in [0.1, 0.3, 0.5, 0.7, 0.9]:
            for ref_fwhm in [0.8, 1., 1.3]:
                for new_fwhm in [1., 1.3, 1.9, 2.5]:
                    for m1 in [0.4, 1., 1.54]:
                        for m2 in [0.1, 0.25]:
                            for px_scale in [0.3, 0.7, 1.1, 1.5]:
                                for l in [0, 90, 180, 270]:
                                    for b in [10, 30, 60]:
                                        for ref_back_sbright in [20., 21., 22.]:
                                            for new_back_sbright in [20, 19., 18]:

                                        confs = {
                                                 'ref_starzp': ref_starzp,
                                                 'ref_starslope': ref_slope,
                                                 'ref_fwhm': ref_fwhm,
                                                 'new_fwhm': new_fwhm,
                                                 'm1_diam': m1,
                                                 'm2_diam': m2,
                                                 'l': l,
                                                 'b':b,
                                                 'eff_col': (3.14/4.)*(m1**2 - m2**2),
                                                 'px_scale': px_scale,
                                                 'ref_back_sbright' : ref_back_sbright,
                                                 'new_back_sbright' : new_back_sbright
                                                 }
                                        SIM_CUBE.append(confs)
    with open('sim_cube.pkl', 'wb') as fp:
        ujson.dump(SIM_CUBE, fp)
