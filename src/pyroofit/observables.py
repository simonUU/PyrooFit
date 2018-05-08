# -*- coding: utf-8 -*-
""" Observables

    Interface to RooRealVar objects.

"""

import ROOT


def extract_from_list(var):
    """

    Parameters
    ----------
    var : list or tuple
        List or tuple

    Returns
    -------
        name, val, lwb, upb
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


def create_roo_variable(var=None,
                        name='x',
                        title='',
                        lwb=None,
                        upb=None,
                        val=None,
                        unit='',):
    """ Crate a RooRealVar through several ways

    Parameters
    ----------
    var
    name
    title
    lwb
    upb
    val
    unit

    Returns
    -------
        RooRealVar
    """

    if isinstance(var, ROOT.RooRealVar):
        return var

    if isinstance(var, ROOT.RooFormulaVar):
        return var

    # backward compatibility
    if isinstance(var, list) or isinstance(var, tuple):
        name_tmp, lwb, upb, val = extract_from_list(var)
        if name_tmp is not None:
            name = name_tmp
    if title is None:
        title = name

    return ROOT.RooRealVar(name, title, val, lwb, upb, unit)
