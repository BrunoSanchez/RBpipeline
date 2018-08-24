#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at 2016-12-14T10:42:52.224316 by corral 0.0.1


# =============================================================================
# DOCS
# =============================================================================

"""rbogus main loader

"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import run
from . import models
from .scripts import gen_diff
from corral.conf import settings as stgs

# =============================================================================
# LOADER
# =============================================================================

class Load(run.Loader):

    def setup(self):
        last_img = self.session.query(models.Images).order_by(
            models.Images.id.desc()).first()
        self.current_params = None
        if last_img is  not None:
            index = last_img.id
            self.current_index = int(index) + 1
        else:
            self.current_index = 1

        if type(stgs.SIM_CUBE) is str:
            import ujson
            with open(stgs.SIM_CUBE, 'rb') as fp:
                SIM_CUBE = ujson.load(fp)
        else:
            SIM_CUBE = stgs.SIM_CUBE

        self.current_params = SIM_CUBE[
            self.current_index%len(SIM_CUBE)]

        self.session.autocommit = False
        # self.session.buff = []

    def generate(self):
        print('current index {}'.format(self.current_index))
        print('current params', self.current_params)
        results = gen_diff.main(self.current_index, self.current_params)

        diff_path      = results[0]
        detections     = results[1]
        diff_ois_path  = results[2]
        detections_ois = results[3]
        diff_hot_path  = results[4]
        detections_hot = results[5]
        transients     = results[6]
        sdetections    = results[7]
        scorrdetections= results[8]
        times          = results[9]

# =============================================================================
# properimage
# =============================================================================
        image = models.Images()
        image.path = diff_path
        image.ref_starzp = self.current_params['ref_starzp']
        image.ref_starslope = self.current_params['ref_starslope']
        image.ref_fwhm = self.current_params['ref_fwhm']
        image.new_fwhm = self.current_params['new_fwhm']
        image.m1_diam = self.current_params['m1_diam']
        image.m2_diam = self.current_params['m2_diam']
        image.l = self.current_params['l']
        image.b = self.current_params['b']
        image.eff_col = self.current_params['eff_col']
        image.px_scale = self.current_params['px_scale']
        image.ref_back_sbright = self.current_params['ref_back_sbright']
        image.new_back_sbright = self.current_params['new_back_sbright']
        image.crossmatched = False
        image.exec_time = times[0]

        self.session.add(image)
        self.session.commit()

        detections['image_id'] = gen_diff.np.repeat(image.id, len(detections))
        detections.to_sql('Detected', self.session.get_bind(),
                           if_exists='append', index=False)

# =============================================================================
# sdetect
# =============================================================================
        simage = models.SImages()
        simage.path = diff_path
        simage.ref_starzp = self.current_params['ref_starzp']
        simage.ref_starslope = self.current_params['ref_starslope']
        simage.ref_fwhm = self.current_params['ref_fwhm']
        simage.new_fwhm = self.current_params['new_fwhm']
        simage.m1_diam = self.current_params['m1_diam']
        simage.m2_diam = self.current_params['m2_diam']
        simage.l = self.current_params['l']
        simage.b = self.current_params['b']
        simage.eff_col = self.current_params['eff_col']
        simage.px_scale = self.current_params['px_scale']
        simage.ref_back_sbright = self.current_params['ref_back_sbright']
        simage.new_back_sbright = self.current_params['new_back_sbright']
        simage.crossmatched = False
        simage.exec_time = times[0]

        self.session.add(simage)
        self.session.commit()

        sdetections['image_id'] = gen_diff.np.repeat(simage.id, len(sdetections))
        sdetections.to_sql('SDetected', self.session.get_bind(),
                            if_exists='append', index=False)
# =============================================================================
# scorrdetect
# =============================================================================
        scorrimage = models.SCorrImages()
        scorrimage.path = diff_path
        scorrimage.ref_starzp = self.current_params['ref_starzp']
        scorrimage.ref_starslope = self.current_params['ref_starslope']
        scorrimage.ref_fwhm = self.current_params['ref_fwhm']
        scorrimage.new_fwhm = self.current_params['new_fwhm']
        scorrimage.m1_diam = self.current_params['m1_diam']
        scorrimage.m2_diam = self.current_params['m2_diam']
        scorrimage.l = self.current_params['l']
        scorrimage.b = self.current_params['b']
        scorrimage.eff_col = self.current_params['eff_col']
        scorrimage.px_scale = self.current_params['px_scale']
        scorrimage.ref_back_sbright = self.current_params['ref_back_sbright']
        scorrimage.new_back_sbright = self.current_params['new_back_sbright']
        scorrimage.crossmatched = False
        scorrimage.exec_time = times[0]

        self.session.add(scorrimage)
        self.session.commit()

        scorrdetections['image_id'] = gen_diff.np.repeat(scorrimage.id, len(scorrdetections))
        scorrdetections.to_sql('SCorrDetected', self.session.get_bind(),
                            if_exists='append', index=False)
#------------------------------------------------------------------------------
# =============================================================================
# OIS
# =============================================================================
        image_ois = models.ImagesOIS()
        image_ois.path = diff_ois_path
        image_ois.ref_starzp = self.current_params['ref_starzp']
        image_ois.ref_starslope = self.current_params['ref_starslope']
        image_ois.ref_fwhm = self.current_params['ref_fwhm']
        image_ois.new_fwhm = self.current_params['new_fwhm']
        image_ois.m1_diam = self.current_params['m1_diam']
        image_ois.m2_diam = self.current_params['m2_diam']
        image_ois.l = self.current_params['l']
        image_ois.b = self.current_params['b']
        image_ois.eff_col = self.current_params['eff_col']
        image_ois.px_scale = self.current_params['px_scale']
        image_ois.ref_back_sbright = self.current_params['ref_back_sbright']
        image_ois.new_back_sbright = self.current_params['new_back_sbright']
        image_ois.crossmatched = False
        image_ois.exec_time = times[1]

        self.session.add(image_ois)
        self.session.commit()

        detections_ois['image_id'] = gen_diff.np.repeat(image_ois.id,
                                                        len(detections_ois))
        detections_ois.to_sql('DetectedOIS', self.session.get_bind(),
                           if_exists='append', index=False)
#------------------------------------------------------------------------------
# =============================================================================
# HOTPANTS
# =============================================================================
        image_hot = models.ImagesHOT()
        image_hot.path = diff_hot_path
        image_hot.ref_starzp = self.current_params['ref_starzp']
        image_hot.ref_starslope = self.current_params['ref_starslope']
        image_hot.ref_fwhm = self.current_params['ref_fwhm']
        image_hot.new_fwhm = self.current_params['new_fwhm']
        image_hot.m1_diam = self.current_params['m1_diam']
        image_hot.m2_diam = self.current_params['m2_diam']
        image_hot.l = self.current_params['l']
        image_hot.b = self.current_params['b']
        image_hot.eff_col = self.current_params['eff_col']
        image_hot.px_scale = self.current_params['px_scale']
        image_hot.ref_back_sbright = self.current_params['ref_back_sbright']
        image_hot.new_back_sbright = self.current_params['new_back_sbright']
        image_hot.crossmatched = False
        image_hot.exec_time = times[2]

        self.session.add(image_hot)
        self.session.commit()

        detections_hot['image_id'] = gen_diff.np.repeat(image_hot.id,
                                                        len(detections_hot))
        detections_hot.to_sql('DetectedHOT', self.session.get_bind(),
                           if_exists='append', index=False)
#------------------------------------------------------------------------------

        transients['image_id'] = gen_diff.np.repeat(image.id, len(transients))

        transients['simage_id'] = gen_diff.np.repeat(simage.id, len(transients))

        transients['image_id_ois'] = gen_diff.np.repeat(image_ois.id,
                                                        len(transients))
        transients['image_id_hot'] = gen_diff.np.repeat(image_hot.id,
                                                        len(transients))
        # print transients
        transients.to_sql('Simulated', self.session.get_bind(),
                          if_exists='append', index=False)

    def teardown(self, type, value, traceback):
        if not type:
            self.session.commit()

