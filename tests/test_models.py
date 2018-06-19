#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pyroofit.models import Argus, Mbc, Chebychev, DstD0BG

import pandas as pd
import numpy as np


def get_test_df(size=100):
    d = {}
    d['mbc'] = np.random.random_sample(size)
    d['mbc2'] = np.random.random_sample(size)
    return pd.DataFrame(d)


def test_Argus():
    import ROOT
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    pdf = Argus(('mbc', 0, 1))
    pdf.observables.mbc # test that mbc is available by attribute lookup
    pdf.get()
    assert isinstance(pdf.roo_pdf, ROOT.RooArgusBG)


def test_Chebychev():
    import ROOT
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    pdf = Chebychev(('mbc', 0, 1))
    pdf.fix(True)
    #pdf.fit(df)
    #pdf.plot('test.pdf')
    pdf.observables.mbc # test that mbc is available by attribute lookup
    assert isinstance(pdf.roo_pdf, ROOT.RooChebychev)


def test_Mbc():
    import ROOT
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    pdf = Mbc(('mbc', 0, 1))

    pdf.observables.mbc # test that mbc is available by attribute lookup
    assert isinstance(pdf.roo_pdf, ROOT.RooAddPdf)


def test_DstD0BG():
    import ROOT

    pdf = DstD0BG(('mbc', 0, 1))

    assert isinstance(pdf.roo_pdf, ROOT.RooDstD0BG)

