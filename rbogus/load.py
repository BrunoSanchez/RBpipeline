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

class Loader(run.Loader):

    def setup(self):
        index = self.session.query(models.Images.id).order_by(
            models.Images.id.desc()).first()
        if indexes is not None:
            self.current_index = index + 1
        else:
            self.current_index = 0

        self.session.autocommit = False
        # self.session.buff = []

    def generate(self):
        detections = gen_diff.main(self.current_index)


