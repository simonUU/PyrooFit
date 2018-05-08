#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import pandas as pd
import numpy as np
import ROOT

from pyroofit.models import Gauss, Chebychev


def get_test_df(size=100):
    d = {}
    d['mbc1'] = np.random.random_sample(size)
    d['mbc'] = np.random.random_sample(size)
    return pd.DataFrame(d)


def test_PDF_init_list():
    pdf = Chebychev(['mbc', 0, 1])
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_PDF_init_RooRealVar():
    x = ROOT.RooRealVar('mbc', '', 0, 0, 1)
    pdf = Chebychev(x)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_PDF_Gauss():
    x = ROOT.RooRealVar('mbc', '', 0, 0, 1)
    pdf = Gauss(x)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_PDF_Chebychev():
    x = ROOT.RooRealVar('mbc', '', 0, 0, 1)
    pdf = Chebychev(x, n=10)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)

"""
def test_fit():
    x = ROOT.RooRealVar('mbc', '', 0, 0, 1)
    pdf = Gauss(x)
    df = get_test_df(100)
    pdf.fit(df)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)
"""

