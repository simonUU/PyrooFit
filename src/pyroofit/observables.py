# -*- coding: utf-8 -*-
""" Observables

    Involves ROOT - hence it is ugly

"""

import ROOT

from .utilities import AttrDict, check_kwds

""" Some Predefined observables
"""
default_observables = {
    'mbc': ROOT.RooRealVar("mbc", "M_{bc}", 5.27, 5.22, 5.289, "GeV/c^{2}"),
    'mbc2': ROOT.RooRealVar("mbc2", "M_{bc}", 5.27, 5.22, 5.289, "GeV/c^{2}"),
    #'phi': ROOT.RooRealVar("phi", "#phi", 0, ROOT.TMath.Pi(), "rad"),
}


def create_variable(name, lwb, upb, val=None, title=None, unit=None):
    """ fast way to create a variable

    Args:
        name:
        lwb:
        upb:
        val:
        title:
        unit:

    Returns:
        RooRealVar
    """
    if val is None:
        val = (lwb + upb)/2.
    return create_roo_variable(name=name, lwb=lwb, upb=upb, val=val, title=title, unit=unit)


class Var(AttrDict):
    @check_kwds(["title", "lwb", "upb", "val", "unit"])
    def __init__(self, name=None, **kwds):
        if name is None:
            super(Var, self).__init__(**kwds)
        else:
            super(Var, self).__init__(name=name, **kwds)


def create_roo_variable(var=None,
                        name=None,
                        title='',
                        lwb=None,
                        upb=None,
                        val=None,
                        unit='',
                        param_name=None,
                        add_name=''):
    """

    Args:
        var:
        name:
        title:
        lwb:
        upb:
        val:

    Returns:

    """

    if isinstance(var, str):
        var = default_observables.get(var, Var(var))

    if isinstance(var, ROOT.RooRealVar):
        return var

    if isinstance(var, ROOT.RooFormulaVar):
        return var

    if name is None:
        name = param_name

    # backward compatibility
    if isinstance(var, list):
        if len(var) == 2:
            lwb, upb = var
            val = (lwb + upb)/2.
        elif len(var) == 3:
            name, lwb, upb = var
            val = (lwb + upb) / 2.
        elif len(var) == 4:
            name, val, lwb, upb = var
        else:
            assert False, "pleas give variables in the form of [name, lwb, upd]"
        if title is None:
            title = name
        return ROOT.RooRealVar(name, title, val, lwb, upb, unit)

    if isinstance(var, Var):

        name = var.get("name", name) if name is None else name

        title = var.get("title", name)
        unit = var.get('unit', unit)

        lwb = var.get("lwb", lwb)
        if lwb is None:
            lwb = 0

        upb = var.get("upb", upb)
        if upb is None:
            upb = lwb + 1

        val = var.get("val", val)

        if val is None:
            val = (lwb + upb) / 2.0

        name += add_name

    if title is None:
        title = ''

    return ROOT.RooRealVar(name, title, val, lwb, upb, unit)
