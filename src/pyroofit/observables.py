# -*- coding: utf-8 -*-
""" Observables

    Interface to RooRealVar objects.

"""

import ROOT

from .utilities import AttrDict, check_kwds, is_iterable


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



class Var:
    def __init__(self, name=None, min=0, max=1, value=None, title=None, unit=None):
        self.name = name
        self.min = min
        self.max = max
        self.value = value if value is not None else (min + max)/2.
        self.title = title
        self.unit = unit

    def roo(self):
        name = self.name if self.name is not None else "X"
        return ROOT.RooRealVar(name, self.title, self.value, self.min, self.max, self.unit)


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
