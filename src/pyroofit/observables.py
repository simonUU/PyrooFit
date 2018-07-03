# -*- coding: utf-8 -*-
""" Observables

Interface to RooRealVar objects.

Todo:
    * This can be made better, maybe only one function

"""

import ROOT


def extract_from_list(var):
    """ Extract name, min, mean and max from a list

    Args:
        var (list): List in a format like ['x', -1, 1] or (-2, 0, 3)

    Returns:
        name, value, min, max

    """
    var = list(var)
    name = val = lwb = upb = None

    assert len(var) >= 2, "Please use a format like ['x', -1, 1] or (-2, 0, 3)"

    if isinstance(var[0], str):
        name = var[0]
        var = var[1:]
    var = sorted(var)
    if len(var) == 2:
        lwb, upb = var
        val = lwb+upb
        val /= 2.
    if len(var) == 3:
        lwb, val, upb = var

    return name, val, lwb, upb


def create_roo_variable(var=None, name='x', title='', lwb=None, upb=None, val=None, unit=''):
    """ Magic function to convert several objects into ROOT.RooRealVar

    Args:
        var (list or ROOT.RooAbsReal): Variable from list or ROOT object
        name (str): Name of the new ROOT.RooRealVar
        title (str): Title of the new ROOT.RooRealVar
        lwb (float): Lower bound
        upb (float): Upper bound
        val (float): Value
        unit (str): ROOT formatted string containing the unit of the observable

    Returns:
        ROOT.RooRealVar observable

    """
    if isinstance(var, ROOT.RooRealVar):
        return var

    if isinstance(var, ROOT.RooFormulaVar):
        return var

    # backward compatibility
    if isinstance(var, tuple) or isinstance(var, list):
        name_tmp, val, lwb, upb = extract_from_list(var)
        if name_tmp is not None:
            name = name_tmp

    if title is '' or None:
        title = name

    return ROOT.RooRealVar(name, title, val, lwb, upb, unit)
