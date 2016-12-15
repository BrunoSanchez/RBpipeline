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
        index = self.session.query(models.Images.id).order_by(
            models.Images.id.desc()).first()
        if index is not None:
            self.current_index = int(index[0]) + 1
        else:
            self.current_index = 0

        self.session.autocommit = False
        # self.session.buff = []

    def generate(self):
        diff_path, detections, transients = gen_diff.main(self.current_index)

        image = models.Images()
        image.path = diff_path
        image.crossmatched = False
        self.session.add(image)
        self.session.commit()

        detections['image_id'] = gen_diff.np.repeat(image.id, len(detections))
        detections.to_sql('Detected', self.session.get_bind(),
                           if_exists='append', index=False)

        transients['image_id'] = gen_diff.np.repeat(image.id, len(transients))
        transients.to_sql('Simulated', self.session.get_bind(),
                          if_exists='append', index=False)

    def teardown(self, type, value, traceback):
        if not type:
            self.session.commit()



