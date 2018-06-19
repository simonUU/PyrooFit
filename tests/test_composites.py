#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import pandas as pd
import numpy as np

from pyroofit.models import Gauss, Chebychev
from pyroofit.composites import AddPdf, ProdPdf, Convolution


def get_test_df(size=100):
    d = {}
    d['mbc1'] = np.random.random_sample(size)
    d['mbc'] = np.random.random_sample(size)
    return pd.DataFrame(d)


def test_AddPdf():
    import ROOT
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    bkg = Chebychev(('mbc', 0, 1))
    sig = Gauss(('mbc', 0, 1))

    pdf = sig+bkg

    #pdf.fit(df)
    #pdf.plot('test2.pdf')

    assert isinstance(pdf, AddPdf)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_AddPdf_fit():
    import ROOT
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    bkg = Chebychev(('mbc', 0, 1))
    sig = Gauss(('mbc', 0, 1))

    pdf = sig+bkg

    pdf.fit(df)
    #pdf.plot('test2.pdf')

    assert isinstance(pdf, AddPdf)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_ProdPdf():
    import ROOT
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)

    bkg = Chebychev(('mbc', 0, 1))
    sig = Gauss(('mbc', 0, 1))

    pdf = sig*bkg

    assert isinstance(pdf, ProdPdf)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_Convolution():
    import ROOT
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    bkg = Chebychev(('mbc', 0, 1))
    sig = Gauss(('mbc', 0, 1))

    pdf = Convolution(bkg, sig)

    assert isinstance(pdf, Convolution)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)

