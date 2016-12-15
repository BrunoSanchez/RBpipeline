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

class StepCrossMatch(run.Step):

    def setup(self):
        self.imgs_to_process = self.session.query(models.Images).filter(
            models.Images.crossmatched == False).order_by(models.Images.id)

    def generate(self):
        for img in self.imgs_to_process:

            detect_to_cx = self.session.query(models.Detected).filter(
                img.id==models.Detected.image_id).all()

            simul_to_cx = self.session.query(models.Simulated).filter(
                img.id==models.Simulated.image_id).all()

            yield [img, detect_to_cx, simul_to_cx]

    def validate(self, batch_list):
        return isinstance(batch_list, list)

    def process(self, batch_list):

        img, detect_to_cx, simul_to_cx = batch_list
        import ipdb; ipdb.set_trace()
        masterXY = np.empty((len(detect_to_cx), 2), dtype=np.float64)
        ref = detect_to_cx.X_IMAGE




        # your logic here
        pass
