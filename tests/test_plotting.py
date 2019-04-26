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


def test_PDF_plot():
    import ROOT
    pdf = Chebychev(['mbc', 0, 1])
    pdf.fit(get_test_df(100))
    pdf.plot("test.pdf")
    # now see if we came so far
    assert isinstance(pdf.roo_pdf, ROOT.RooAbsPdf)
