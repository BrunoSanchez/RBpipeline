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

# from . import models


# =============================================================================
# STEPS
# =============================================================================

class MyStep(run.Step):

    model = None
    conditions = []

    def process(self, obj):
        # your logic here
        pass
