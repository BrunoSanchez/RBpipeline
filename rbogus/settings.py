#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""RBogus pipeline global settings

"""


import logging
import os
import numpy as np

DEBUG_PROCESS = True

LOG_LEVEL = logging.DEBUG #  INFO DEBUG

LOG_FORMAT = "[RBogus-%(levelname)s @ %(asctime)-15s] %(message)s"

CONNECTION = 'postgresql://jarvis:Bessel0@172.18.122.4:5432/resimulation_docker'
#CONNECTION = 'postgresql://jarvis:Bessel0@toritos:5432/resimu_docker'
#CONNECTION = 'postgresql://jarvis:Bessel0@172.18.123.55:5432/resimulation'
#CONNECTION = 'sqlite:///resimulation-dev.db'

LOADER = "rbogus.load.Load"

PIPELINE_SETUP = "rbogus.pipeline.RBogus"

STEPS = [
    "rbogus.steps.RunSimulations",
    "rbogus.steps.StepCrossMatch",
    "rbogus.steps.StepSCrossMatch",
    "rbogus.steps.StepSCorrCrossMatch",
    "rbogus.steps.StepCrossMatchOIS",
    "rbogus.steps.StepCrossMatchHOT",
    "rbogus.steps.SanitizeImages",
    "rbogus.steps.SanitizeSImages",
    "rbogus.steps.SanitizeSCorrImages",
    "rbogus.steps.SanitizeImagesHOT",
    "rbogus.steps.SanitizeImagesOIS"
]

ALERTS = []

# This values are autoimported when you open the shell
SHELL_LOCALS = {
    "np": np
}

PATH = os.path.abspath(os.path.dirname(__file__))

try:
    from .local_settings import *  # noqa
    # print "Local settings file found"
except ImportError:
    print("Local settings not found, using settings.py defaults")
    #~ WORK_DIR = os.path.join(os.path.dirname(__file__), "data")
    #~ PAWPRINT_PATH = os.path.join(WORK_DIR, "inputdata")
    #~ DATA_PATH = os.path.join(WORK_DIR, "outputdata")
