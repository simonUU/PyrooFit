# -*- coding: utf-8 -*-
""" PDF base class

The pdf base class is the main interface to ROOT.
This class basically serves as a wrapper around
AbsPDF of the Roofit package and takes monitors and initiates
observables and parmeters.

Examples
--------

    class MyPDF(PDF):
        def __init__(self, x, param, name='MyPDF'):
            super(MyPDF, self).__init__(name=name, **kwds)

            self._add_observable("x", x)

            self._add_parameter("param1" param)

            self.roo_pdf = ROOT.MyPDF(self.name, self.title, self.observables('x'), self.parameters.para1)


"""


from __future__ import print_function

from .utilities import ClassLoggingMixin, AttrDict, check_kwds
from .data import df2roo
from .dirty.plotting import pull_plot
from .observables import Var, create_roo_variable

import ROOT
from uncertainties import ufloat


class PDF(ClassLoggingMixin, object):
    """Python Meta class for a ROOT.RooAbsPDF"""

    def __init__(self, name, observables=None, title='PDF', **kwds):
        super(PDF, self).__init__(**kwds)

        #: Unique identifier of the PDF
        self.name = name

        #: Title of the PDF
        self.title = title

        #: dict(str->ROOT.RooRealVar) - Input variable form the data frame
        self.observables = AttrDict()
        if observables:
            for observable in observables:
                self._add_observable(observable)

        #: dict(str->ROOT.RooRealVar) - Fitted parameters from the fit procedure
        self.params = AttrDict()

        #: RooAbsPDF
        self.roo_pdf = None
        self.init_pdf()

        self.last_data = None
        self.last_fit = None

        # Fit options
        self.use_minos = True
        self.use_hesse = True
        self.use_extended = False
        self.use_sumw2error = True
        self.print_level = -1

    def __call__(self):
        return self.roo_pdf

    def __add__(self, other):
        from .composits import AddPdf
        return AddPdf([self, other])

    def __mul__(self, other):
        from .composits import  ProdPdf
        return ProdPdf([self, other])

    def init_pdf(self):
        """ Initiate attributes for parameters

        """
        for p in self.params:
            self.__setattr__(p, self.params[p])

    def _add_parameter(self, param_var, param_name=None, name=None, **kwds):
        """ Internal method to add a parameter to the pdf

        Args:
            param_var:
            param_name:
            name:
            **kwds:

        Returns:

        """
        roo_param = create_roo_variable(param_var, name=name, param_name=param_name, **kwds)
        if param_name is None:
            param_name = roo_param.GetName()
        self.params[param_name] = roo_param
        self.__setattr__(param_name, roo_param)
        return roo_param

    def _add_observable(self, observable_var, **kwds):
        roo_observable = create_roo_variable(observable_var, **kwds)
        name = roo_observable.GetName()
        self.observables[name] = roo_observable
        return roo_observable

    def get_fit_data(self, df, weights=None, observables=None):
        """ Transforms DataFrame to a RooDataSet

        Args:
            df:
            weights:
            observables:

        """
        if observables is None:
            observables = self.observables
        roo_data = df2roo(df, columns=observables, weights=weights)
        return roo_data

    def fit(self, df, weights=None, observables=None):
        """ Fit the DataFrame to the PDF

        Args:
            df:
            weights:
            observables:

        """
        self.logger.debug("Fitting")
        self.last_data = self.get_fit_data(df, weights=weights, observables=observables)
        self._fit(self.last_data)

    def _before_fit(self, *args, **kwargs):
        """ Template function before fit

        Args:
            *args:
            **kwargs:
        """
        pass

    def _fit(self, data_roo):
        """ Internal fit function

        Args:
            data_roo (RooDataSet): Dataset to fit on the internal RooAbsPdf

        """
        self._before_fit()
        self.logger.warn("Performing actual fit")
        self.last_fit = self.roo_pdf.fitTo(data_roo,
                                           ROOT.RooFit.Save(True),
                                           ROOT.RooFit.Warnings(ROOT.kFALSE),
                                           #ROOT.RooFit.PrintLevel(-1),
                                           ROOT.RooFit.PrintEvalErrors(-1),
                                           ROOT.RooFit.Extended(self.use_extended),
                                           ROOT.RooFit.SumW2Error(self.use_sumw2error),
                                           ROOT.RooFit.Minos(self.use_minos),
                                           ROOT.RooFit.Hesse(self.use_hesse),)



    def plot(self, filename, data=None, observable=None, *args, **kwargs):
        """ Default Plot function

        Args:
            filename:
            observable:
            *args:
            **kwargs:

        Returns:

        """
        if self.last_data is None and data is None:
            self.logger.error("There is no fit data")
            return

        if data is not None:
            import pandas as pd
            if isinstance(data, pd.DataFrame):
                data = self.get_fit_data(data, observable)

        # suffix
        suffix = filename.split('.')[-1]
        # remove suffix from filename
        if '.' + suffix in filename:
            filename = filename.split('.' + suffix)[0]

        # Find the observable in case there are more observables
        if observable is None:
            if len(self.observables) == 1:
                observable = self.get_observable()
            else:
                for o in self.observables:
                    try:
                        self.logger.info('Plotting ' + o)
                        self._plot(filename + '_' + o + '.' + suffix,  self.observables[o], data, *args, **kwargs)
                    except AttributeError:
                        self.logger.error("There was a plotting error")
                return
        else:
            if type(observable) is str:
                for o in self.observables:
                    if observable == self.observables[o].GetName():
                        observable = self.observables[o]
                        break

        self._plot(filename + '.' + suffix , observable, data, *args, **kwargs)

    def _plot(self, filename, observable, data=None, *args, **kwargs):
        """ plot function to be overwritten

        Args:
            filename:
            observable:
            *args:
            **kwargs:
        """
        if data is None:
            data = self.last_data
        pull_plot(self.roo_pdf, data, observable, filename, *args, **kwargs)

    def _get_var(self, v):
        mes = self.params[v]
        val = mes.getVal()
        # Now catch RooFormulaVar
        try:
            err = mes.getError()
        except AttributeError:
            try:
                err = mes.getPropagatedError(self.last_fit)
            except TypeError:
                err = 0
        return ufloat(val, err)

    def get(self, parameter=None):
        """ Get one of the fitted parameter or print all if None is set

        Args:
            parameter: name of the parameter

        Returns:
            (ufloat) value and error of the parameter

        """

        if parameter is None:
            for m in self.params:
                print('{0:18} ==> {1}'.format(m, self._get_var(m)))
        else:
            return self._get_var(parameter)

    def get_observable(self):
        """ Get the observables from self.observables

        """
        assert len(self.observables) > 0, "There is not obsrvable"
        if len(self.observables) > 1:
            self.logger.warn('There are more than one observables, returning first')

        for value in self.observables.values():
            return value

    def fix(self, constant=True):
        """ Fix all parameters of the PDF

        Args:
            constant:

        Returns:

        """
        for m in self.params:
            self.logger.debug("Setting %s constant" % m)
            self.params[m].setConstant(constant)

    def constrain(self, sigma):
        """ Constrain parameters within given significance
        use only with existing fit result

        Args:
            sigma:

        Returns:

        """
        for m in self.params:
            cent = self.params[m].getVal()
            err = self.params[m].getError()
            self.params[m].setMin(cent-sigma*err)
            self.params[m].setMax(cent + sigma * err)

    def narrow(self, sigma):
        """ Narrows all parameters within one sigma of the original definition"""
        for m in self.params:
            l = self.params[m].getMin()
            h = self.params[m].getMax()
            v = self.params[m].getVal()
            e = self.params[m].getError()

            new_h = v+sigma*e if v+sigma*e < h else h
            new_l = v - sigma * e if v - sigma * e > l else l

            self.params[m].setMax(new_h)
            self.params[m].setMin(new_l)

    def randomize_pdf(self, frac=1/6., exceptions=None, only=None):
        """ Randomize parameters of a pdf

        Args:
            pdf (PDF): Pdf objcet
            frac: with of the Gauss added to each member
        """
        import random
        params = self.params if only is None else only
        for m in params:
            if exceptions is not None:
                if m in exceptions:
                    continue
            try:
                max_ = self.params[m].getMax()
                min_ = self.params[m].getMin()
                dist = abs(max_ - min_)
                to_add = random.normalvariate(0, dist * frac)
                val = self.params[m].getVal()
                if min_ < (val + to_add) < max_:
                    # only a small gaussian blur
                    self.params[m].setVal(val + to_add)
                else:
                    self.params[m].setVal(random.uniform(min_, max_))
            except AttributeError:
                self.logger.error("Unable to randomize parameter " + m)

    def refit(self, randomize=False, exceptions=None, only=None):
        if randomize:
            self.randomize_pdf(exceptions=exceptions, only=only)
        self._fit(self.last_data)

    def check_convergence(self, err_lim_low, err_lim_high, n_refit=20,
                          only=None, exceptions=None, assym=False, ignore_n=True):
        """

        Args:
            err_lim_lowm:
            err_lim_high:
            n_refit:

        Returns:

        """
        passing = True
        suspect = None
        suspect_value = None
        suspect_error = None

        params = only
        if only is None:
            params = [p for p in self.params]

        for p in params:
            if exceptions is not None:
                if p in exceptions:
                    continue
            if ignore_n and 'n_' in p:
                continue
            p_err = self.params[p].getError()
            if assym:
                p_err = min(abs(self.params[p].getErrorHi()), abs(self.params[p].getErrorLo()))
            if not err_lim_low < p_err < err_lim_high:
                passing = False
                suspect = p
                suspect_value = self.params[p].getVal()
                suspect_error = p_err
                break

        if not passing:
            self.logger.error("Fit not converged due to %s (%.4f +-%.4f), try %d refitting "%(suspect,  suspect_value, suspect_error, n_refit))
            if n_refit == 0:
                return False
            else:
                self.refit(randomize=True, exceptions=exceptions, only=only)

                return self.check_convergence(err_lim_low, err_lim_high, n_refit - 1, only=only, exceptions=exceptions, assym=assym)
        return True

    def get_paramameters(self, par_name=None):
        """

        Returns:

        """
        ret = {}
        for p in self.params:

            if par_name is not None:
                if par_name not in p:
                    continue

            par = self.params[p]

            ret[p] = [par.getVal(), par.getError(), par.getMin(), par.getMax()]

        return ret

    def set_parameter(self, p, params):
        """

        Args:
            p:
            params:

        Returns:

        """

        print(p)

        assert p in self.params.keys(), 'Parameter not found'

        par = self.params[p]
        if not isinstance(params, list):
            params = [params]
        if len(params) == 1:
            par.setVal(params[0])
        elif len(params) == 2:
            par.setVal(params[0])
            par.setError(params[1])
        elif len(params) == 4:
            par.setVal(params[0])
            par.setError(params[1])
            par.setMin(params[2])
            par.setMax(params[3])
        else:
            self.error("Could not set parameter")

    def set_parameters(self, pars):
        """

        Args:
            pars:

        Returns:

        """

        for p in pars:
            ps1 = p.split('_')
            if not len(ps1) >= 2:
                self.warn("Parameter %s can not be set" % p)
                continue
            name_remote = ps1[-1]

            for sp in self.params:
                ps2 = sp.split('_')
                if not len(ps2) >= 2:
                    self.warn("Parameter %s can not be set" % sp)
                    continue
                name_self = ps2[-1]
                if name_remote in name_self:
                    self.debug("Setting parameter %s in %s" % (p, sp))
                    self.set_parameter(sp, pars[p])
