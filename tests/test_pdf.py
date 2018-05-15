#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import pandas as pd
import numpy as np

from pyroofit.models import Gauss, Chebychev


def get_test_df(size=100):
    d = {}
    d['mbc1'] = np.random.random_sample(size)
    d['mbc'] = np.random.random_sample(size)
    return pd.DataFrame(d)


def test_PDF_init_list():
    import ROOT
    pdf = Chebychev(['mbc', 0, 1])
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_PDF_init_RooRealVar():
    import ROOT
    x = ROOT.RooRealVar('mbc', '', 0, 0, 1)
    pdf = Chebychev(x)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_PDF_Gauss():
    import ROOT
    x = ROOT.RooRealVar('mbc', '', 0, 0, 1)
    pdf = Gauss(x)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_PDF_Chebychev():
    import ROOT
    x = ROOT.RooRealVar('mbc', '', 0, 0, 1)
    pdf = Chebychev(x, n=10)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_fit():
    import ROOT
    x = ROOT.RooRealVar('mbc', '', 0, 0, 1)
    pdf = Gauss(x)
    df = get_test_df(100)
    pdf.fit(df)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_fit_bins():
    import ROOT
    x = ROOT.RooRealVar('mbc', '', 0, 0, 1)
    pdf = Gauss(x)
    df = get_test_df(100)
    pdf.fit(df, nbins=5)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)

