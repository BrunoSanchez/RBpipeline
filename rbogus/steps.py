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
from . import util as u


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
        IDs = u.matching(detect_to_cx, simul_to_cx)

        for i in range(len(IDs)):
            if IDs[i]>0:
                real = models.Reals()
                real.detected_id = IDs[i]
                real.simulated = simul_to_cx[i]
                self.session.add(real)
            else:
                und = models.Undetected()
                und.simulated = simul_to_cx[i]
                self.session.add(und)

        for detect in detect_to_cx:
            if detect.id not in IDs:
                bogus = models.Bogus()
                bogus.detected = detect
                self.session.add(bogus)

                detect.IS_REAL = False
            else:
                detect.IS_REAL = True

        img.crossmatched = True


class StepCrossMatchOIS(run.Step):

    def setup(self):
        self.imgs_to_process = self.session.query(models.ImagesOIS).filter(
            models.ImagesOIS.crossmatched == False).order_by(models.ImagesOIS.id)

    def generate(self):
        for img in self.imgs_to_process:

            detect_to_cx = self.session.query(models.DetectedOIS).filter(
                img.id==models.DetectedOIS.image_id).all()

            simul_to_cx = self.session.query(models.Simulated).filter(
                img.id==models.Simulated.image_id_ois).all()

            yield [img, detect_to_cx, simul_to_cx]

    def validate(self, batch_list):
        return isinstance(batch_list, list)

    def process(self, batch_list):

        img, detect_to_cx, simul_to_cx = batch_list
        IDs = u.matching(detect_to_cx, simul_to_cx)

        for i in range(len(IDs)):
            if IDs[i]>0:
                real = models.RealsOIS()
                real.detected_id = IDs[i]
                real.simulated = simul_to_cx[i]
                self.session.add(real)
            else:
                und = models.UndetectedOIS()
                und.simulated = simul_to_cx[i]
                self.session.add(und)

        for detect in detect_to_cx:
            if detect.id not in IDs:
                bogus = models.BogusOIS()
                bogus.detected = detect
                self.session.add(bogus)

                detect.IS_REAL = False
            else:
                detect.IS_REAL = True

        img.crossmatched = True


class StepCrossMatchHOT(run.Step):

    def setup(self):
        self.imgs_to_process = self.session.query(models.ImagesHOT).filter(
            models.ImagesHOT.crossmatched == False).order_by(models.ImagesHOT.id)

    def generate(self):
        for img in self.imgs_to_process:

            detect_to_cx = self.session.query(models.DetectedHOT).filter(
                img.id==models.DetectedHOT.image_id).all()

            simul_to_cx = self.session.query(models.Simulated).filter(
                img.id==models.Simulated.image_id_hot).all()

            yield [img, detect_to_cx, simul_to_cx]

    def validate(self, batch_list):
        return isinstance(batch_list, list)

    def process(self, batch_list):

        img, detect_to_cx, simul_to_cx = batch_list
        IDs = u.matching(detect_to_cx, simul_to_cx)

        for i in range(len(IDs)):
            if IDs[i]>0:
                real = models.RealsHOT()
                real.detected_id = IDs[i]
                real.simulated = simul_to_cx[i]
                self.session.add(real)
            else:
                und = models.UndetectedHOT()
                und.simulated = simul_to_cx[i]
                self.session.add(und)

        for detect in detect_to_cx:
            if detect.id not in IDs:
                bogus = models.BogusHOT()
                bogus.detected = detect
                self.session.add(bogus)

                detect.IS_REAL = False
            else:
                detect.IS_REAL = True

        img.crossmatched = True
