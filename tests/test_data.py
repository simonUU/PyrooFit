#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pyroofit.data import df2roo

import pandas as pd
import numpy as np


def get_test_df(size=100):
    d = {}
    d['col1'] = np.random.random_sample(size)
    d['col2'] = np.random.random_sample(size)
    return pd.DataFrame(d)


def test_df2roo():
    import ROOT
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    df_roo = df2roo(df)
    assert isinstance(df_roo, ROOT.RooDataSet)


def test_df2roo_columns():
    import ROOT
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    df_roo = df2roo(df, columns=['col1'])
    assert isinstance(df_roo, ROOT.RooDataSet)


def test_df2roo_observables():
    import ROOT
    df = get_test_df()
    assert isinstance(df, pd.DataFrame)
    obs = {}
    obs['col1'] = ROOT.RooRealVar('col1','',0,1)
    obs['col2'] = ROOT.RooRealVar('col2', '', 0, 1)
    df_roo = df2roo(df, observables=obs)
    assert isinstance(df_roo, ROOT.RooDataSet)


def test_df2roo_weights_array():
    import ROOT
    df = get_test_df()
    w = np.random.uniform(0, 1, len(df))

    df_roo = df2roo(df, weights=w)
    df_roo.Print()
    assert isinstance(df_roo, ROOT.RooDataSet)


def test_df2roo_weights_columnname():
    import ROOT
    df = get_test_df()
    df['w'] = np.random.uniform(0, 1, len(df))

    df_roo = df2roo(df, weights='w')
    df_roo.Print()
    assert isinstance(df_roo, ROOT.RooDataSet)


def test_roo2hist():
    import ROOT
    df = get_test_df()
    df['w'] = np.random.uniform(0, 1, len(df))

    hist = df2roo(df, columns=['col1'], bins=20)
    assert isinstance(hist, ROOT.RooDataHist)

