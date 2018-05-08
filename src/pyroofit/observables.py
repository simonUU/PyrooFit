# -*- coding: utf-8 -*-
""" Observables

    Interface to RooRealVar objects.

"""

import ROOT

from .utilities import AttrDict, check_kwds, is_iterable


def create_variable(name, min, max, val=None, title=None, unit=None):
    """ Fast method to create a RooRealVar

    Parameters
    ----------
    name
    min
    max
    val
    title
    unit

    Returns
    -------
    RooRealVar

    """
    if val is None:
        if min > max:
            print("WARNING min > max")
        val = (min + max)/2.
    return create_roo_variable(name=name, min=min, max=max, val=val, title=title, unit=unit)


class Var(AttrDict):
    @check_kwds(["title", "min", "max", "val", "unit"])
    def __init__(self, name=None, **kwds):
        if name is None:
            super(Var, self).__init__(**kwds)
        else:
            super(Var, self).__init__(name=name, **kwds)


@check_kwds(["title", "min", "max", "val", "unit"])
def to_var(var, **kwds):
    """ Fast conversion from list to Variable

    Parameters
    ----------
    var : list or dict
        List or dictionary containing the variable like ['name', min, max]
    kwds

    Returns
    -------

    """
    if isinstance(var, list):
        name = val = lwb = upb = None
        if len(var) == 2:
            lwb, upb = var
            val = (lwb + upb)/2.
        elif len(var) == 3:
            name, lwb, upb = var
            val = (lwb + upb) / 2.
        elif len(var) == 4:
            name, val, lwb, upb = var
        return Var(name, lwb, upb, val)
    else:
        return Var(**kwds)


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
            name, lwb, upb, val = var
        else:
            assert False, "pleas give variables in the form of [name, min, max, (val)]"
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
