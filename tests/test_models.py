#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pyroofit.models import Argus, Mbc, Chebychev, Var

import pandas as pd
import numpy as np
import ROOT


def get_test_df(size=100):
    d = {}
    d['mbc'] = np.random.random_sample(size)
    d['mbc2'] = np.random.random_sample(size)
    return pd.DataFrame(d)


def test_Argus():
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    pdf = Argus(Var('mbc', lwb=0, upb=1))
    pdf.observables.mbc # test that mbc is available by attribute lookup
    pdf.get()
    assert isinstance(pdf.roo_pdf, ROOT.RooArgusBG)


def test_Chebychev():
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    pdf = Chebychev(Var('mbc', lwb=0, upb=1))
    pdf.fix(True)
    pdf.fit(df)
    pdf.plot('test.pdf')
    pdf.observables.mbc # test that mbc is available by attribute lookup
    assert isinstance(pdf.roo_pdf, ROOT.RooChebychev)


def test_Mbc():
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    pdf = Mbc(Var('mbc', lwb=0, upb=1))

    pdf.observables.mbc # test that mbc is available by attribute lookup
    assert isinstance(pdf.roo_pdf, ROOT.RooAddPdf)
