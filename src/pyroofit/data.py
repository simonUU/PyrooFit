# -*- coding: utf-8 -*-
""" Conversion between Root and python

"""

from __future__ import print_function

from root_numpy import array2tree
import ROOT
import pandas as pd
import numpy as np

def roo2hist(roo, binning, obs, name, observables=None):
    """

    Parameters
    ----------
    roo
    binning
    obs
    name
    observables

    Returns
    -------

    """

    obs.setBins(binning)

    if observables is None:
        observables = ROOT.RooArgSet()
        observables.add(obs)

    hist = ROOT.RooDataHist("Name","Data Hist", observables, roo)

    return hist



def df2roo(df, observables=None, columns=None, name='data', weights=None, ownership=True, bins=None):
    """Convert a DataFrame into a RooDataSet
    The `column` parameters select features of the DataFrame which should be included in the RooDataSet.

    Parameters
    ----------
    df : DataFrame or array
        Input data to be transformed to a RooDataSet
    observables : dict
        Dictionary of observables to convert data with the correct range of the observables of interest
    columns : :obj:`list` of :obj:`str`, optional
        List of column names of the DataFrame
    name : :obj:`str`
        Name of the Dataset should be unique to avoid problems with ROOT
    weights : :obj:`str` or array, optional
        Name or values of weights to assign weights to the RooDataSet
    ownership : bool, optional
        Experimental, True for ROOT garbage collection
    bins : int
        creates RooDataHist instead with specified number of bins

    Returns
    -------
    RooDataSet
        A conversion of the DataFrame

    """

    # Return DataFrame object
    if isinstance(df, ROOT.RooDataSet):
        return df

    # TODO Convert Numpy Array
    if not isinstance(df, pd.DataFrame):
        print("Did not receive DataFrame")
        assert observables is not None, "Did not receive an observable "
        assert len(observables) == 1, "Can only handle 1d array, use pd.DataFrame instead"
        assert len(np.array(df).shape) == 1, "Can only handle 1d array, use pd.DataFrame instead"
        d = {list(observables.keys())[0]: np.array(df)}
        df = pd.DataFrame(d)

    # Gather columns in the DataFrame to be included in the rooDataSet
    if columns is None:
        if observables is not None:
            columns = [observables[v].GetName() for v in observables]
    if columns is not None:
        for v in columns:
            assert v in df.columns, "Variable %s not in DataFrame" % v
    else:
        columns = df.columns

    df_subset = df[columns]

    # Add weights into roofit format
    if weights is not None:
        if isinstance(weights, str):
            df_subset['w'] = df[weights]
        else:
            assert len(weights) == len(df), "Strange length of the weights"
            df_subset['w'] = weights
        # Check if weights are normalized
        w = df_subset['w']
        if len(w) != int(np.sum(w)):
            #print("Oh no I have to renormalize , %d, %f"%(len(w), np.sum(w)))
            df_subset['w'] *= len(w)/float(np.sum(w))
            #print("now it is %f"%np.sum(df_subset['w']))

    # Check for NaN values
    if df_subset.isnull().values.any():
        df_subset = df_subset.dropna()
        print("NaN Warning")

    # WARNING: possible memory leak
    df_tree = array2tree(df_subset.to_records())
    ROOT.SetOwnership(df_tree, ownership)

    roo_argset = ROOT.RooArgSet()
    roo_var_list = []  # Hast to exist due to the python2 garbage collector

    if observables is None:
        for c in columns:
            v = ROOT.RooRealVar(c, c, df_subset[c].mean(),   df_subset[c].min(), df_subset[c].max(), )
            roo_var_list.append(v)

            roo_argset.add(v)
    else:
        for v in observables:
            roo_argset.add(observables[v])
            roo_var_list.append(observables[v])

    # Create final roofit data-set
    if weights is not None:
        w = ROOT.RooRealVar('w', 'Weights', df_subset['w'].mean(), df_subset['w'].min(), df_subset['w'].max(), )
        roo_argset.add(w)
        roo_var_list.append(w)
        df_roo = ROOT.RooDataSet(name, name, roo_argset, ROOT.RooFit.Import(df_tree), ROOT.RooFit.WeightVar(w),)
    else:
        df_roo = ROOT.RooDataSet(name, name, roo_argset, ROOT.RooFit.Import(df_tree),)
    ROOT.SetOwnership(df_roo, ownership)

    if bins is not None:
        return roo2hist(df_roo, bins, roo_var_list[0], name, roo_argset)

    return df_roo
