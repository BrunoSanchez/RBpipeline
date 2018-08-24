"""Local settings for rbpipeline"""

PATH = "/home/bruno/Data/NewRBpipeline/output"

#~ IMGS_PATH = '/home/bruno/Data/NewRBpipeline/images'
#~ CONFIG_PATH = '/home/bruno/Data/NewRBpipeline/config'
#~ CATS_PATH = '/home/bruno/Data/NewRBpipeline/cats'

#IMGS_PATH = '/mnt/is0/bos0109/data_sim_O2/images'
#CONFIG_PATH = '/mnt/is0/bos0109/data_sim_O2/config'
#CATS_PATH = '/mnt/is0/bos0109/data_sim_O2/cats'


import os

CUBE = 'sim_cube.json'

if os.path.isfile(CUBE):
    print('reading cube')
    SIM_CUBE = os.path.abspath(CUBE)

else:
    print('generating cube')
    SIM_CUBE = []

    #for ref_starzp in [4e3, 8e3, 16e3, 32e3, 64e3]:
    ref_starzp = 16e3
        #for ref_starslope in [0.1, 0.4, 0.6, 0.9]:
    ref_starslope = 0.4
            #for ref_fwhm in [0.8, 1., 1.3]:
    ref_fwhm = 1.
                    #for m1 in [0.4, 1., 1.54]:
    m1 = 1.
                        #for m2 in [0.1, 0.25]:
    m2 = 0.1
    for new_fwhm in [1., 1.3, 1.9, 2.5]:
        for px_scale in [0.3, 0.7, 1.4]:
            for l in [60, 180, 300]:
                for b in [10, 30, 60]:
                    for ref_back_sbright in [20., 21., 22.]:
                        for new_back_sbright in [20, 19., 18]:
                            confs = {
                             'ref_starzp': ref_starzp,
                             'ref_starslope': ref_starslope,
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
    #import ipdb; ipdb.set_trace()
    import ujson
    with open(CUBE, 'wb') as fp:
        ujson.dump(SIM_CUBE, fp)
