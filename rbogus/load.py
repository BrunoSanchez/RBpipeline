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
from scripts import gen_diff

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
            if self.current_index%100 is 0:
                self.current_params = {'zp'   : last_img.refstarcount_zp*2.,
                                       'slope': last_img.refstarcount_slope+0.1,
                                       'fwhm' : last_img.refseeing_fwhm+0.1}
            else:
                self.current_params = {'zp'   : last_img.refstarcount_zp,
                                       'slope': last_img.refstarcount_slope,
                                       'fwhm' : last_img.refseeing_fwhm}
        else:
            self.current_index = 1
            self.current_params = {'zp'   : 2e3,
                                   'slope': 0.1,
                                   'fwhm' : 0.8}

        self.session.autocommit = False
        # self.session.buff = []

    def generate(self):
        print 'current index {}'.format(self.current_index)
        print 'current params', self.current_params
        results = gen_diff.main(self.current_index, **self.current_params)

        diff_path      = results[0]
        detections     = results[1]
        diff_ois_path  = results[2]
        detections_ois = results[3]
        diff_hot_path  = results[4]
        detections_hot = results[5]
        transients     = results[6]

# =============================================================================
# properimage
# =============================================================================
        image = models.Images()
        image.path = diff_path
        image.refstarcount_zp = self.current_params['zp']
        image.refstarcount_slope = self.current_params['slope']
        image.refseeing_fwhm = self.current_params['fwhm']
        image.crossmatched = False

        self.session.add(image)
        self.session.commit()

        detections['image_id'] = gen_diff.np.repeat(image.id, len(detections))
        detections.to_sql('Detected', self.session.get_bind(),
                           if_exists='append', index=False)
#------------------------------------------------------------------------------
# =============================================================================
# OIS
# =============================================================================
        image_ois = models.ImagesOIS()
        image_ois.path = diff_ois_path
        image_ois.crossmatched = False

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
        image_hot.crossmatched = False

        self.session.add(image_hot)
        self.session.commit()

        detections_hot['image_id'] = gen_diff.np.repeat(image_hot.id,
                                                        len(detections_hot))
        detections_hot.to_sql('DetectedHOT', self.session.get_bind(),
                           if_exists='append', index=False)
#------------------------------------------------------------------------------

        transients['image_id'] = gen_diff.np.repeat(image.id, len(transients))

        transients['image_id_ois'] = gen_diff.np.repeat(image_ois.id,
                                                        len(transients))
        transients['image_id_hot'] = gen_diff.np.repeat(image_hot.id,
                                                        len(transients))

        transients.to_sql('Simulated', self.session.get_bind(),
                          if_exists='append', index=False)

    def teardown(self, type, value, traceback):
        if not type:
            self.session.commit()



