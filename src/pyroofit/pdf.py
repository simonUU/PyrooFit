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

            self.add_observable(x)

            self.add_parameter(param)

            self.roo_pdf = ROOT.MyPDF(self.name, self.title, self.observables('x'), self.parameters.para1)


"""


from __future__ import print_function

from .utilities import ClassLoggingMixin, AttrDict
from .data import df2roo
from .plotting import fast_plot
from .observables import create_roo_variable

import ROOT


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
                self.add_observable(observable)

        #: dict(str->ROOT.RooRealVar) - Fitted parameters from the fit procedure
        self.parameters = AttrDict()
        self.parameter_names = AttrDict()

        #: RooAbsPDF
        self.roo_pdf = None
        self.init_pdf()

        self.last_data = None
        self.last_fit = None

        # Fit options
        self.use_minos = False
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
        from .composits import ProdPdf
        return ProdPdf([self, other])

    def init_pdf(self):
        """ Initiate attributes for parameters

        """
        for p in self.parameters:
            self.__setattr__(p, self.parameters[p])

    def add_parameter(self, param_var, param_name, final_name=None, **kwds):
        """ Add Parameter

        Parameters
        ----------
        param_name
        param_var
        final_name
        kwds

        Returns
        -------
        RooRealVar
            converted RooRealVar
        """

        if final_name is None:
            name = self.name + '_' + param_name
        else:
            name = final_name
        roo_param = create_roo_variable(param_var, name=name, **kwds)
        self.parameters[param_name] = roo_param
        self.__setattr__(param_name, roo_param)
        return self.parameters[param_name]

    def add_observable(self, observable_var, **kwds):

        if isinstance(observable_var, list) or isinstance(observable_var, tuple):
            if not isinstance(observable_var[0], str):
                print("WARNING : choosing automatic variable name 'x'")

        roo_observable = create_roo_variable(observable_var, **kwds)
        name = roo_observable.GetName()
        self.observables[name] = roo_observable
        return self.observables[name]

    def get_fit_data(self, df, weights=None, observables=None, nbins=None):
        """ Transforms DataFrame to a RooDataSet

        Args:
            df:
            weights:
            observables:

        """
        if observables is None:
            observables = self.observables

        roo_data = df2roo(df, observables=observables, weights=weights, bins=nbins)
        return roo_data

    def fit(self, df, weights=None, nbins=None):
        """

        Parameters
        ----------
        df
        weights
        nbins

        Returns
        -------

        """

        self.logger.debug("Fitting")
        self.last_data = self.get_fit_data(df, weights=weights, nbins=nbins)
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
                data = self.get_fit_data(data)

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
        fast_plot(self.roo_pdf, data, observable, filename, *args, **kwargs)

    def _get_var(self, v, as_ufloat=False):
        mes = self.parameters[v]
        val = mes.getVal()
        # Now catch RooFormulaVar
        try:
            err = mes.getError()
        except AttributeError:
            try:
                err = mes.getPropagatedError(self.last_fit)
            except TypeError:
                err = 0
        if not as_ufloat:
            return val, err
        try:
            from uncertainties import ufloat
            return ufloat(val, err)
        except ImportError:
            return val, err



    def get(self, parameter=None, as_ufloat=False):
        """ Get one of the fitted parameter or print all if None is set

        Args:
            parameter: name of the parameter

        Returns:
            (ufloat) value and error of the parameter

        """

        if parameter is None:
            for m in self.parameters:
                print('{0:18} ==> {1}'.format(m, self._get_var(m, True)))
        else:
            return self._get_var(parameter, as_ufloat)

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
        for m in self.parameters:
            self.logger.debug("Setting %s constant" % m)
            self.parameters[m].setConstant(constant)

    def constrain(self, sigma):
        """ Constrain parameters within given significance
        use only with existing fit result

        Args:
            sigma:

        Returns:

        """
        for m in self.parameters:
            cent = self.parameters[m].getVal()
            err = self.parameters[m].getError()
            self.parameters[m].setMin(cent - sigma * err)
            self.parameters[m].setMax(cent + sigma * err)

    def narrow(self, sigma):
        """ Narrows all parameters within one sigma of the original definition"""
        for m in self.parameters:
            l = self.parameters[m].getMin()
            h = self.parameters[m].getMax()
            v = self.parameters[m].getVal()
            e = self.parameters[m].getError()

            new_h = v+sigma*e if v+sigma*e < h else h
            new_l = v - sigma * e if v - sigma * e > l else l

            self.parameters[m].setMax(new_h)
            self.parameters[m].setMin(new_l)

    def randomize_pdf(self, frac=1/6., exceptions=None, only=None):
        """ Randomize parameters of a pdf

        Args:
            pdf (PDF): Pdf objcet
            frac: with of the Gauss added to each member
        """
        import random
        params = self.parameters if only is None else only
        for m in params:
            if exceptions is not None:
                if m in exceptions:
                    continue
            try:
                max_ = self.parameters[m].getMax()
                min_ = self.parameters[m].getMin()
                dist = abs(max_ - min_)
                to_add = random.normalvariate(0, dist * frac)
                val = self.parameters[m].getVal()
                if min_ < (val + to_add) < max_:
                    # only a small gaussian blur
                    self.parameters[m].setVal(val + to_add)
                else:
                    self.parameters[m].setVal(random.uniform(min_, max_))
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
            params = [p for p in self.parameters]

        for p in params:
            if exceptions is not None:
                if p in exceptions:
                    continue
            if ignore_n and 'n_' in p:
                continue
            p_err = self.parameters[p].getError()
            if assym:
                p_err = min(abs(self.parameters[p].getErrorHi()), abs(self.parameters[p].getErrorLo()))
            if not err_lim_low < p_err < err_lim_high:
                passing = False
                suspect = p
                suspect_value = self.parameters[p].getVal()
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
        for p in self.parameters:

            if par_name is not None:
                if par_name not in p:
                    continue

            par = self.parameters[p]

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

        assert p in self.parameters.keys(), 'Parameter not found'

        par = self.parameters[p]
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

            for sp in self.parameters:
                ps2 = sp.split('_')
                if not len(ps2) >= 2:
                    self.warn("Parameter %s can not be set" % sp)
                    continue
                name_self = ps2[-1]
                if name_remote in name_self:
                    self.debug("Setting parameter %s in %s" % (p, sp))
                    self.set_parameter(sp, pars[p])
