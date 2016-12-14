#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created at 2016-12-14T10:42:52.224316 by corral 0.0.1


# =============================================================================
# DOCS
# =============================================================================

"""rbogus steps

"""


# =============================================================================
# IMPORTS
# =============================================================================

from corral import run

from . import models


# =============================================================================
# STEPS
# =============================================================================

class CrossMatch(run.Step):

    mod_image = models.Image
    mod_detected = models.Detected
    mod_simulated = models.Simulated

    def setup(self):
        imgs_to_process = self.session.query(mod_image).filter(
            mod_image.crossmatched == False).order_by(mod_image.id.desc())

    def generate(self):
        for img in imgs_to_process:
            detect_to_cx = self.session.query(mod_detected).filter(
                img.id==mod_detected.image_id).all()
            simul_to_cx = self.session.query(mod_simulated).filter(
                img.id==mod_detected.image_id).all()
            yield [img, detect_to_cx, simul_to_cx]

    def process(self, batch_list):


        # your logic here
        pass
