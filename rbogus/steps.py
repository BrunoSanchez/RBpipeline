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
import numpy as np
from joblib import Parallel, delayed
from .scripts import gen_diff

# =============================================================================
# STEPS
# =============================================================================

class RunSimulations(run.Step):

    def generate(self):
        sims = list(self.session.query(models.Simulation).filter_by(executed=False))
        sims = np.array(sims)
        size = int(len(sims) / 16) or 1
        for i_chunk, chunk in enumerate(np.array_split(sims, size)):
            if i_chunk<21:
                yield chunk
            else:
                break


    def validate(self, batch_list):
        return isinstance(batch_list, np.ndarray)

    def as_dict(self, a_sim):
        params = {k: getattr(a_sim, k) for k in a_sim.__table__.c.keys()}
        params["path"] = a_sim.path
        return params

    def process(self, batch_list):
        bp = map(self.as_dict, batch_list)

        #~ self.gen_and_load(bp[0])

        with Parallel(n_jobs=4) as jobs:
            batch_res = jobs(
                delayed(gen_diff.main)(params)
                for params in bp)

        for results, params, asim in zip(batch_res, bp, batch_list):

            if results == 'error101':
                asim.executed = True
                asim.failed_to_subtract = True
                asim.possible_saturation = True
                continue

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

            # =====================================================================
            # properimage
            # =====================================================================
            image = models.Images()
            image.path = params['path']
            image.simulation = asim
            image.crossmatched = False
            image.exec_time = times[0]

            self.session.add(image)
            self.session.commit()

            detections['image_id'] = np.repeat(image.id, len(detections))
            detections.to_sql('Detected', self.session.get_bind(),
                               if_exists='append', index=False)

            # ==================================================================
            # sdetect
            # ==================================================================
            simage = models.SImages()
            simage.path = params['path']
            simage.simulation_id = params['id']
            simage.crossmatched = False
            simage.exec_time = times[0]

            self.session.add(simage)
            self.session.commit()

            #import ipdb; ipdb.set_trace()
            sdetections['image_id'] = np.repeat(simage.id, len(sdetections))
            sdetections['xmin_col'] = sdetections['xmin']
            sdetections['xmax_col'] = sdetections['xmax']
            sdetections.drop(['xmin', 'xmax'], axis=1, inplace=True)
            sdetections.to_sql('SDetected', self.session.get_bind(),
                                if_exists='append', index=False)

            # =====================================================================
            # scorrdetect
            # =====================================================================
            scorrimage = models.SCorrImages()
            scorrimage.path = params['path']
            scorrimage.simulation_id = params['id']
            scorrimage.crossmatched = False
            scorrimage.exec_time = times[0]

            self.session.add(scorrimage)
            self.session.commit()

            scorrdetections['image_id'] = np.repeat(scorrimage.id, len(scorrdetections))
            scorrdetections.to_sql('SCorrDetected', self.session.get_bind(),
                                if_exists='append', index=False)

            # =====================================================================
            # OIS
            # =====================================================================
            image_ois = models.ImagesOIS()
            image_ois.path = params['path']
            image_ois.simulation_id = params['id']
            image_ois.crossmatched = False
            image_ois.exec_time = times[1]

            self.session.add(image_ois)
            self.session.commit()

            detections_ois['image_id'] = np.repeat(image_ois.id, len(detections_ois))
            detections_ois.to_sql('DetectedOIS', self.session.get_bind(),
                               if_exists='append', index=False)

            # =====================================================================
            # HOTPANTS
            # =====================================================================
            image_hot = models.ImagesHOT()
            image_hot.path = diff_hot_path
            image_hot.crossmatched = False
            image_hot.exec_time = times[2]

            self.session.add(image_hot)
            self.session.commit()

            detections_hot['image_id'] = np.repeat(image_hot.id, len(detections_hot))
            detections_hot.to_sql('DetectedHOT', self.session.get_bind(),
                               if_exists='append', index=False)

            #----------------------------------------------------------------------

            transients['image_id'] = np.repeat(image.id, len(transients))

            transients['simage_id'] = np.repeat(simage.id, len(transients))

            transients['image_id_ois'] = np.repeat(image_ois.id, len(transients))
            transients['image_id_hot'] = np.repeat(image_hot.id, len(transients))
            # print transients
            transients.to_sql('Simulated', self.session.get_bind(),
                              if_exists='append', index=False)

            asim.executed = True
            asim.failed_to_subtract = False
            asim.possible_saturation = False



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
        if len(detect_to_cx) is 0:
            print('no detections')
            for asim in simul_to_cx:
                und = models.Undetected()
                und.simulated = asim
                self.session.add(und)
            img.crossmatched = True
            return

        IDs = u.matching(detect_to_cx, simul_to_cx, radius=2.)

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


class StepSCrossMatch(run.Step):

    def setup(self):
        self.imgs_to_process = self.session.query(models.SImages).filter(
            models.SImages.crossmatched == False).order_by(models.SImages.id)

    def generate(self):
        for img in self.imgs_to_process:

            detect_to_cx = self.session.query(models.SDetected).filter(
                img.id==models.SDetected.image_id).all()

            simul_to_cx = self.session.query(models.Simulated).filter(
                img.id==models.Simulated.image_id).all()

            yield [img, detect_to_cx, simul_to_cx]

    def validate(self, batch_list):
        return isinstance(batch_list, list)

    def process(self, batch_list):

        img, detect_to_cx, simul_to_cx = batch_list
        if len(detect_to_cx) is 0:
            print('no detections')
            for asim in simul_to_cx:
                und = models.Undetected()
                und.simulated = asim
                self.session.add(und)
            img.crossmatched = True
            return

        IDs = u.matching(detect_to_cx, simul_to_cx, sep=True, radius=2.5)

        for i in range(len(IDs)):
            if IDs[i]>0:
                real = models.SReals()
                real.detected_id = IDs[i]
                real.simulated = simul_to_cx[i]
                self.session.add(real)
            else:
                und = models.SUndetected()
                und.simulated = simul_to_cx[i]
                self.session.add(und)

        for detect in detect_to_cx:
            if detect.id not in IDs:
                bogus = models.SBogus()
                bogus.detected = detect
                self.session.add(bogus)

                detect.IS_REAL = False
            else:
                detect.IS_REAL = True

        img.crossmatched = True


class StepSCorrCrossMatch(run.Step):

    def setup(self):
        self.imgs_to_process = self.session.query(models.SCorrImages).filter(
            models.SCorrImages.crossmatched == False).order_by(models.SCorrImages.id)

    def generate(self):
        for img in self.imgs_to_process:

            detect_to_cx = self.session.query(models.SCorrDetected).filter(
                img.id==models.SCorrDetected.image_id).all()

            simul_to_cx = self.session.query(models.Simulated).filter(
                img.id==models.Simulated.image_id).all()

            yield [img, detect_to_cx, simul_to_cx]

    def validate(self, batch_list):
        return isinstance(batch_list, list)

    def process(self, batch_list):

        img, detect_to_cx, simul_to_cx = batch_list
        if len(detect_to_cx) is 0:
            print('no detections')
            for asim in simul_to_cx:
                und = models.Undetected()
                und.simulated = asim
                self.session.add(und)
            img.crossmatched = True
            return

        IDs = u.matching(detect_to_cx, simul_to_cx, radius=2.5)

        for i in range(len(IDs)):
            if IDs[i]>0:
                real = models.SCorrReals()
                real.detected_id = IDs[i]
                real.simulated = simul_to_cx[i]
                self.session.add(real)
            else:
                und = models.SCorrUndetected()
                und.simulated = simul_to_cx[i]
                self.session.add(und)

        for detect in detect_to_cx:
            if detect.id not in IDs:
                bogus = models.SCorrBogus()
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
        if len(detect_to_cx) is 0:
            print('no detections')
            for asim in simul_to_cx:
                und = models.Undetected()
                und.simulated = asim
                self.session.add(und)
            img.crossmatched = True
            return

        IDs = u.matching(detect_to_cx, simul_to_cx, radius=2.)

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
        if len(detect_to_cx) is 0:
            print('no detections')
            for asim in simul_to_cx:
                und = models.Undetected()
                und.simulated = asim
                self.session.add(und)
            img.crossmatched = True
            return
        IDs = u.matching(detect_to_cx, simul_to_cx, radius=2.)

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
