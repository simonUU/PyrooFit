#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pyroofit.data import df2roo

import pandas as pd
import numpy as np
import ROOT

from pyroofit.pdf import AddPdf, ProdPdf, Convolution, Var
from pyroofit.models import Gauss, Chebychev


def get_test_df(size=100):
    d = {}
    d['mbc1'] = np.random.random_sample(size)
    d['mbc'] = np.random.random_sample(size)
    return pd.DataFrame(d)


def test_PDF_init_Var():
    pdf = Chebychev(Var('mbc', lwb=0, upb=1))
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_PDF_init_list():
    pdf = Chebychev(['mbc', 0, 1])
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_PDF_init_str():
    pdf = Chebychev('mbc')
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_AddPdf():
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    bkg = Chebychev(Var('mbc', lwb=0, upb=1))
    sig = Gauss(Var('mbc', lwb=0, upb=1))

    pdf = sig+bkg

    pdf.fit(df)
    pdf.plot('test2.pdf')

    assert isinstance(pdf, AddPdf)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_ProdPdf():
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)

    bkg = Chebychev(Var('mbc', lwb=0, upb=1))
    sig = Gauss(Var('mbc', lwb=0, upb=1))

    pdf = sig*bkg

    assert isinstance(pdf, ProdPdf)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


def test_Convolution():
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    bkg = Chebychev(Var('mbc', lwb=0, upb=1))
    sig = Gauss(Var('mbc', lwb=0, upb=1))

    pdf = Convolution(bkg, sig)

    assert isinstance(pdf, Convolution)
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)


