#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This module contains the table model definitions for toritos database.
# It uses the sqlalchemy orm to define the column structures

import os
import shutil

from corral import db
from corral.conf import settings


class Simulated(db.Model):
    """Model for transients that are simulated"""

    __tablename__ = "Simulated"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, nullable=True)
    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    app_mag = db.Column(db.Float, nullable=False)

    image_id = db.Column(db.Integer, db.ForeignKey('Images.id'))
    image = db.relationship('Images',
                            backref=db.backref('simulateds', order_by=id))

    image_id_ois = db.Column(db.Integer, db.ForeignKey('ImagesOIS.id'))
    image_ois = db.relationship('ImagesOIS',
                            backref=db.backref('simulateds', order_by=id))

    def __repr__(self):
        return str(self.id)



# =============================================================================
# Propersubtract tables
# =============================================================================
class Images(db.Model):

    __tablename__ = "Images"

    id = db.Column(db.Integer, primary_key=True)

    path = db.Column(db.String(100), nullable=False)

    crossmatched = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return self.path


class Reals(db.Model):

    __tablename__ = "Reals"

    id = db.Column(db.Integer, primary_key=True)

    detected_id = db.Column(db.Integer, db.ForeignKey('Detected.id'))
    detected = db.relationship('Detected',
                               backref=db.backref('true_pos', order_by=id))

    simulated_id = db.Column(db.Integer, db.ForeignKey('Simulated.id'))
    simulated = db.relationship('Simulated',
                                backref=db.backref('true_pos'), order_by=id)

    def __repr__(self):
        return str(self.id)


class Bogus(db.Model):

    __tablename__ = "Bogus"

    id = db.Column(db.Integer, primary_key=True)

    detected_id = db.Column(db.Integer, db.ForeignKey('Detected.id'))
    detected = db.relationship('Detected',
                               backref=db.backref('true_neg', order_by=id))

    def __repr__(self):
        return str(self.id)


class Undetected(db.Model):

    __tablename__ = "Undetected"

    id = db.Column(db.Integer, primary_key=True)

    simulated_id = db.Column(db.Integer, db.ForeignKey('Simulated.id'))
    simulated = db.relationship('Simulated',
                                backref=db.backref('false_neg', order_by=id))

    def __repr__(self):
        return str(self.id)


class Detected(db.Model):

    __tablename__ = "Detected"

    id = db.Column(db.Integer, primary_key=True)

    NUMBER = db.Column(db.Integer, nullable=False)
    FLUX_ISO = db.Column(db.Float, nullable=False)
    FLUXERR_ISO = db.Column(db.Float, nullable=False)
    MAG_ISO = db.Column(db.Float, nullable=False)
    MAGERR_ISO = db.Column(db.Float, nullable=False)
    FLUX_APER = db.Column(db.Float, nullable=False)
    FLUXERR_APER = db.Column(db.Float, nullable=False)
    MAG_APER = db.Column(db.Float, nullable=False)
    MAGERR_APER = db.Column(db.Float, nullable=False)
    FLUX_AUTO = db.Column(db.Float, nullable=False)
    FLUXERR_AUTO = db.Column(db.Float, nullable=False)
    MAG_AUTO = db.Column(db.Float, nullable=False)
    MAGERR_AUTO = db.Column(db.Float, nullable=False)
    BACKGROUND = db.Column(db.Float, nullable=False)
    THRESHOLD = db.Column(db.Float, nullable=False)
    FLUX_MAX = db.Column(db.Float, nullable=False)
    XMIN_IMAGE = db.Column(db.Float, nullable=False)
    YMIN_IMAGE = db.Column(db.Float, nullable=False)
    XMAX_IMAGE = db.Column(db.Float, nullable=False)
    YMAX_IMAGE = db.Column(db.Float, nullable=False)
    XPEAK_IMAGE = db.Column(db.Float, nullable=False)
    YPEAK_IMAGE = db.Column(db.Float, nullable=False)
    X_IMAGE = db.Column(db.Float, nullable=False)
    Y_IMAGE = db.Column(db.Float, nullable=False)
    X2_IMAGE = db.Column(db.Float, nullable=False)
    Y2_IMAGE = db.Column(db.Float, nullable=False)
    XY_IMAGE = db.Column(db.Float, nullable=False)
    CXX_IMAGE = db.Column(db.Float, nullable=False)
    CYY_IMAGE = db.Column(db.Float, nullable=False)
    CXY_IMAGE = db.Column(db.Float, nullable=False)
    A_IMAGE = db.Column(db.Float, nullable=False)
    B_IMAGE = db.Column(db.Float, nullable=False)
    THETA_IMAGE = db.Column(db.Float, nullable=False)
    MU_MAX = db.Column(db.Float, nullable=False)
    FLAGS = db.Column(db.Float, nullable=False)
    FWHM_IMAGE = db.Column(db.Float, nullable=False)
    ELONGATION = db.Column(db.Float, nullable=False)
    ELLIPTICITY = db.Column(db.Float, nullable=False)
    CLASS_STAR = db.Column(db.Float, nullable=False)

    DELTAX = db.Column(db.Float, nullable=False)
    DELTAY = db.Column(db.Float, nullable=False)
    RATIO = db.Column(db.Float, nullable=False)
    ROUNDNESS = db.Column(db.Float, nullable=False)
    PEAK_CENTROID = db.Column(db.Float, nullable=False)
    IS_REAL = db.Column(db.Boolean, nullable=True)

    image_id = db.Column(db.Integer, db.ForeignKey('Images.id'))
    image = db.relationship('Images',
                            backref=db.backref('detected_srcs', order_by=id))

    def __repr__(self):
        return '{}::{}'.format(self.image, self.NUMBER)


# =============================================================================
# OIS tables
# =============================================================================
class ImagesOIS(db.Model):

    __tablename__ = "ImagesOIS"

    id = db.Column(db.Integer, primary_key=True)

    path = db.Column(db.String(100), nullable=False)

    crossmatched = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return self.path


class DetectedOIS(db.Model):

    __tablename__ = "DetectedOIS"

    id = db.Column(db.Integer, primary_key=True)

    NUMBER = db.Column(db.Integer, nullable=False)
    FLUX_ISO = db.Column(db.Float, nullable=False)
    FLUXERR_ISO = db.Column(db.Float, nullable=False)
    MAG_ISO = db.Column(db.Float, nullable=False)
    MAGERR_ISO = db.Column(db.Float, nullable=False)
    FLUX_APER = db.Column(db.Float, nullable=False)
    FLUXERR_APER = db.Column(db.Float, nullable=False)
    MAG_APER = db.Column(db.Float, nullable=False)
    MAGERR_APER = db.Column(db.Float, nullable=False)
    FLUX_AUTO = db.Column(db.Float, nullable=False)
    FLUXERR_AUTO = db.Column(db.Float, nullable=False)
    MAG_AUTO = db.Column(db.Float, nullable=False)
    MAGERR_AUTO = db.Column(db.Float, nullable=False)
    BACKGROUND = db.Column(db.Float, nullable=False)
    THRESHOLD = db.Column(db.Float, nullable=False)
    FLUX_MAX = db.Column(db.Float, nullable=False)
    XMIN_IMAGE = db.Column(db.Float, nullable=False)
    YMIN_IMAGE = db.Column(db.Float, nullable=False)
    XMAX_IMAGE = db.Column(db.Float, nullable=False)
    YMAX_IMAGE = db.Column(db.Float, nullable=False)
    XPEAK_IMAGE = db.Column(db.Float, nullable=False)
    YPEAK_IMAGE = db.Column(db.Float, nullable=False)
    X_IMAGE = db.Column(db.Float, nullable=False)
    Y_IMAGE = db.Column(db.Float, nullable=False)
    X2_IMAGE = db.Column(db.Float, nullable=False)
    Y2_IMAGE = db.Column(db.Float, nullable=False)
    XY_IMAGE = db.Column(db.Float, nullable=False)
    CXX_IMAGE = db.Column(db.Float, nullable=False)
    CYY_IMAGE = db.Column(db.Float, nullable=False)
    CXY_IMAGE = db.Column(db.Float, nullable=False)
    A_IMAGE = db.Column(db.Float, nullable=False)
    B_IMAGE = db.Column(db.Float, nullable=False)
    THETA_IMAGE = db.Column(db.Float, nullable=False)
    MU_MAX = db.Column(db.Float, nullable=False)
    FLAGS = db.Column(db.Float, nullable=False)
    FWHM_IMAGE = db.Column(db.Float, nullable=False)
    ELONGATION = db.Column(db.Float, nullable=False)
    ELLIPTICITY = db.Column(db.Float, nullable=False)
    CLASS_STAR = db.Column(db.Float, nullable=False)

    DELTAX = db.Column(db.Float, nullable=False)
    DELTAY = db.Column(db.Float, nullable=False)
    RATIO = db.Column(db.Float, nullable=False)
    ROUNDNESS = db.Column(db.Float, nullable=False)
    PEAK_CENTROID = db.Column(db.Float, nullable=False)
    IS_REAL = db.Column(db.Boolean, nullable=True)

    image_id = db.Column(db.Integer, db.ForeignKey('ImagesOIS.id'))
    image = db.relationship('ImagesOIS',
                            backref=db.backref('detected_srcs', order_by=id))

    def __repr__(self):
        return '{}::{}'.format(self.image, self.NUMBER)


class RealsOIS(db.Model):

    __tablename__ = "RealsOIS"

    id = db.Column(db.Integer, primary_key=True)

    detected_id = db.Column(db.Integer, db.ForeignKey('DetectedOIS.id'))
    detected = db.relationship('DetectedOIS',
                               backref=db.backref('true_pos_ois', order_by=id))

    simulated_id = db.Column(db.Integer, db.ForeignKey('Simulated.id'))
    simulated = db.relationship('Simulated',
                                backref=db.backref('true_pos_ois'), order_by=id)

    def __repr__(self):
        return str(self.id)


class UndetectedOIS(db.Model):

    __tablename__ = "UndetectedOIS"

    id = db.Column(db.Integer, primary_key=True)

    simulated_id = db.Column(db.Integer, db.ForeignKey('Simulated.id'))
    simulated = db.relationship('Simulated',
                                backref=db.backref('false_neg_ois', order_by=id))

    def __repr__(self):
        return str(self.id)


class BogusOIS(db.Model):

    __tablename__ = "BogusOIS"

    id = db.Column(db.Integer, primary_key=True)

    detected_id = db.Column(db.Integer, db.ForeignKey('DetectedOIS.id'))
    detected = db.relationship('DetectedOIS',
                               backref=db.backref('true_neg_ois', order_by=id))

    def __repr__(self):
        return str(self.id)
