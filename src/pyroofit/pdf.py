# -*- coding: utf-8 -*-
""" PDF base class

The pdf base class is the main interface to ROOT. This class basically serves as a wrapper around AbsPDF of
the Roofit package and takes, monitors and initiates observables and parameters.

Examples:

    How to add a new wrapper to a ROOT.AbsPdf:

    :code:``
    class MyPDF(PDF):
        def __init__(self, x, param, name='MyPDF'):
            super(MyPDF, self).__init__(name=name, **kwds)

            x = self.add_observable(x)

            param1 = self.add_parameter(param)

            self.roo_pdf = ROOT.MyPDF(self.name, self.title, x, param1)``


"""

from __future__ import print_function

import ROOT

from .utilities import ClassLoggingMixin, AttrDict
from .data import df2roo
from .plotting import fast_plot
from .observables import create_roo_variable


class PDF(ClassLoggingMixin, object):
    """ Base class for the ROOT.RooFit wrapper

    Attributes:
        name (str): Name of the pdf
        title (str) Title of the pdf, displayed automatically in the legend
        observables (dict): Dictionary of the fit observables
        parameters (dict): Dictionary of the fit parameters
        roo_pdf (:obj:`ROOT.RooAbsPdf`): Basis ROOT.RooFit object of the wrapper
        last_data (:obj:`ROOT.RooAbsData`): Reference to last fit data
        last_fit: Reference to last fit result

    Todo:
        * Maybe remove observables key
        * Add convolution to @ overwrite?

    """

    def __init__(self, name, observables=None, title='PDF', **kwds):
        """ Init of the PDF class

        Args:
            name (:obj:`str`): Name of the model
            observables (:obj:`list` of :obj:`ROOT.RooRealVar`, optional): Deprecated
            title (:obj:`str`): Title of the model
            **kwds: >> May be removed

        """
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

        #: bool: Fit options for minuit
        self.use_minos = False
        self.use_hesse = True
        self.use_extended = False
        self.use_sumw2error = True

        #: int: Flag for the ROOT output
        self.print_level = -1

    def __call__(self):
        """ Call overwrite

        Returns:
            ROOT.RooAbsPdf base model

        """
        return self.roo_pdf

    def __add__(self, other):
        """ Add operator overwrite

        Args:
            other (:obj:`PDF`): Pdf to be added

        Returns:
            AddPdf of the two PDF objects

        """
        from .composites import AddPdf
        return AddPdf([self, other])

    def __mul__(self, other):
        """ Mul operator overwrite

        Returns:
            ProdPdf

        """
        from .composites import ProdPdf
        return ProdPdf([self, other])

    def init_pdf(self):
        """ Initiate attributes for parameters

        """
        for p in self.parameters:
            self.__setattr__(p, self.parameters[p])

    def add_parameter(self, param_var, param_name=None, final_name=None, **kwds):
        """ Add fit parameter

        Args:
            param_var (list or ROOT.RooRealVar): Initialisation of the parameter as list or ROOT object
            param_name (:obj:`str`): Name of the parameter within the object (Not within ROOT namespace!)
            final_name (:obj:`str`, optional): Name if the parameter within PDF and ROOT namespace
            **kwds: create_roo_variable keywords

        Returns:
            ROOT.RooRealVar reference to fit parameter

        """
        if final_name is None:
            assert param_name is not None, "Please specify a parameter name"
            name = self.name + '_' + param_name
        else:
            name = final_name
        roo_param = create_roo_variable(param_var, name=name, **kwds)
        self.parameters[param_name] = roo_param
        self.parameter_names[param_name] = name
        self.__setattr__(param_name, roo_param)
        return self.parameters[param_name]

    def add_observable(self, observable_var, **kwds):
        """ Addidng a observable to the PDF

        Observables are used in the PDF class to convert relevant columns in pandas.DataFrames

        Args:
            observable_var (list or ROOT.RooRealVar): Initialisation of the observable as list or ROOT object
            **kwds: create_roo_variable keywords

        Returns:
            ROOT.RooRealVar reference to fit observable

        """
        if isinstance(observable_var, list) or isinstance(observable_var, tuple):
            if not isinstance(observable_var[0], str):
                self.warn("WARNING : choosing automatic variable name 'x'")

        roo_observable = create_roo_variable(observable_var, **kwds)
        name = roo_observable.GetName()
        self.observables[name] = roo_observable
        return self.observables[name]

    def get_fit_data(self, df, weights=None, observables=None, nbins=None, *args, **kwargs):
        """ Convert pandas.DataFrame to ROOT.RooAbsData containing only relevant columns

        Args:
            df (:obj:`DataFrame` or :obj:`array`): Fit data
            weights (:obj:`str` or :obj:`array`, optional): Column name of weights or wrights data
            observables (dict, optional): Dictionary of the observables to be converted
            nbins (int, optional): Number of bins, created ROOT.RooDataHist instead

        Returns:
            ROOT.RooDataSet or ROOT.RooDataHist of relevant columns and rows of the input data

        """
        if observables is None:
            observables = self.observables

        roo_data = df2roo(df, observables=observables, weights=weights, bins=nbins, *args, **kwargs)
        return roo_data

    def fit(self, df, weights=None, nbins=None, *args, **kwargs):
        """ Fit a pandas or numpy data to the PDF

        Args:
            df (:obj:`DataFrame` or :obj:`array`): Fit data
            weights (:obj:`str` or :obj:`array`, optional): Column name of weights or wrights data
            nbins (int, optional): Number of bins, created ROOT.RooDataHist instead

        Returns:
            ROOT.RooFitResult of the fit

        """
        self.logger.debug("Fitting")
        self.last_data = self.get_fit_data(df, weights=weights, nbins=nbins, *args, **kwargs)
        self._fit(self.last_data)

    def _before_fit(self, *args, **kwargs):
        """ Template function before fit

        This function is called before the fit and can be overwritten for certain use cases.
        """
        pass

    def _fit(self, data_roo):
        """ Internal fit function

        Args:
            data_roo (ROOT.RooDataSet): Dataset to fit on the internal RooAbsPdf

        """
        self._before_fit()
        self.logger.info("Performing fit")
        self.last_fit = self.roo_pdf.fitTo(data_roo,
                                           ROOT.RooFit.Save(True),
                                           ROOT.RooFit.Warnings(ROOT.kFALSE),
                                           ROOT.RooFit.PrintLevel(self.print_level),
                                           ROOT.RooFit.PrintEvalErrors(-1),
                                           ROOT.RooFit.Extended(self.use_extended),
                                           ROOT.RooFit.SumW2Error(self.use_sumw2error),
                                           ROOT.RooFit.Minos(self.use_minos),
                                           ROOT.RooFit.Hesse(self.use_hesse),)

    def plot(self, filename, data=None, observable=None, *args, **kwargs):
        """ Default plotting function

        Args:
            filename (str): Name of the output file. Suffix determines file type.
            data (DataFrame or ROOT.RooDataSet, optional): Data to be plotted in the fit
            observable (:obj:`ROOT.RooAbsReal` or str, optional): In case of multiple dimensions draw
                projection to specified observable.
            *args: Arguments for fast_plot
            **kwargs: Keyword arguments for fast_plot

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
        self._plot(filename + '.' + suffix, observable, data, *args, **kwargs)

    def _plot(self, filename, observable, data=None, *args, **kwargs):
        """ plot function to be overwritten
        Args:
            filename (str): Name of the output file. Suffix determines file type.
            data (DataFrame or ROOT.RooDataSet, optional): Data to be plotted in the fit
            observable (:obj:`ROOT.RooAbsReal` or str, optional): In case of multiple dimensions draw
                projection to specified observable.
            *args: Arguments for fast_plot
            **kwargs: Keyword arguments for fast_plot

        """
        if data is None:
            data = self.last_data
        fast_plot(self.roo_pdf, data, observable, filename, *args, **kwargs)

    def _get_var(self, v, as_ufloat=False):
        """ Internal getter for parameter values

        Args:
            v: Parameter name
            as_ufloat: Return ufolat object

        Returns:
            :obj:`tuple` or :obj:`ufloat` mean and error of parameter
        """
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
            ret = ufloat(val, err)
            return ret
        except ImportError:
            return val, err

    def get(self, parameter=None, as_ufloat=False):
        """ Get one of the fitted parameter or print all if None is set

        Args:
            parameter (str): name of the parameter
            as_ufloat (bool, optional): If true return ufloat object, else tuple

        Returns:
            :obj:`tuple` or :obj:`ufloat` mean and error of parameter

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
            constant (bool, default=True): Set all parameter constant

        """
        for m in self.parameters:
            self.logger.debug("Setting %s constant" % m)
            self.parameters[m].setConstant(constant)

    def constrain(self, sigma):
        """ Constrain parameters within given significance
        use only with existing fit result

        Args:
            sigma (int or float): Interval to constrain parameter is convidence of the error.

        """
        for m in self.parameters:
            cent = self.parameters[m].getVal()
            err = self.parameters[m].getError()
            self.parameters[m].setMin(cent - sigma * err)
            self.parameters[m].setMax(cent + sigma * err)

    def narrow(self, sigma=1):
        """ Narrows all parameters within one sigma of the original definition, keeps original limits

        Args:
            sigma (int or float): Interval to constrain parameter is convidence of the error.

        """
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
            frac: with of the Gauss added to each member
            exceptions (list): List of excluded parameters
            only (list): List of parameters to include

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
        """ Check convergence of PDF and refit

        Args:
            err_lim_low:
            err_lim_high:
            n_refit:
            only:
            exceptions:
            assym:
            ignore_n:

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
            self.warn("Fit not converged due to %s (%.4f +-%.4f),"
                      " try %d refitting " % (suspect, suspect_value, suspect_error, n_refit))
            if n_refit == 0:
                return False
            else:
                self.refit(randomize=True, exceptions=exceptions, only=only)

                return self.check_convergence(err_lim_low,
                                              err_lim_high,
                                              n_refit - 1,
                                              only=only,
                                              exceptions=exceptions,
                                              assym=assym)
        return True

    def get_parameters(self, par_name=None):
        """ Get values for parameter

        Args:
            par_name (str, optional): Parameter name

        Returns:
            list of [mean, error, min, max]

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
        """ Set parameter to value, error and limits, Experimental

        Args:
            p (str): Name of the parameter
            params (list): [value, error=optional, min=optional, max=optional]

        """
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
        """ Set parameters in the pdf, Experimental

        Args:
            pars (list of lists):

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

    def get_curve(self, observable=None, npoints=1000):
        """ Get projection of the pdf curve

        Args:
            observable (str, optional): Name of the observable
            npoints (int): number of points, default=1000

        Returns:
            hx, hy : numpy arrays of x and y points of the pdf projection


        Examples:
            >>> import matplotlib.pyplot as plt
            >>> plt.plot(*pdf.get_curve())

        """
        import root_numpy
        import numpy as np

        if observable is not None:
            assert isinstance(observable, str), "please specify the name of the observable"
            assert observable in self.observables, "observable not found"
        else:
            observable = self.get_observable().GetName()
        h = self.roo_pdf.createHistogram(observable, npoints)
        hy, hx = root_numpy.hist2array(h, False, False, True)
        # Normalise y
        hy = npoints * hy / np.sum(hy)
        # center x
        hx = (hx[0][:-1] + hx[0][1:])/2.

        return hx, hy

    def get_fwhm(self, observable=None, npoints=1000):
        """ Calculate Full width at half maximum - EXPERIMENTAL

        Args:
            observable
            npoints

        Returns:
            FWHM


        """

        if observable is not None:
            assert isinstance(observable, str), "please specify the name of the observable"
            assert observable in self.observables, "observable not found"
        else:
            observable = self.get_observable().GetName()
        h = self.roo_pdf.createHistogram(observable, npoints)
        bin1 = h.FindFirstBinAbove(h.GetMaximum()/2.)
        bin2 = h.FindLastBinAbove(h.GetMaximum()/2.)
        fwhm = h.GetBinCenter(bin2) - h.GetBinCenter(bin1)
        return fwhm