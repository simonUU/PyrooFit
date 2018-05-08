# -*- coding: utf-8 -*-
""" Fit models predefined

    In this module  all the predifined models are defined.


"""


from .pdf import PDF
from .composits import AddPdf, ProdPdf
from .observables import Var, create_roo_variable

import ROOT


class Gauss(PDF):
    """ Standard gaussian

    """
    def __init__(self,
                 observable,
                 mean=Var(min=-1, max=1),
                 sigma=Var(min=0, max=1),
                 name='gauss_sig',
                 title='Gaussian PDF',
                 **kwds):

        super(Gauss, self).__init__(name=name, title=title, **kwds)

        self._add_observable(observable)

        self._add_parameter(mean, "mean")
        self._add_parameter(sigma, "sigma")

        self.roo_pdf = ROOT.RooGaussian(name, title, self.get_observable(), self.params['mean'], self.params['sigma'])


class BifurGauss(PDF):
    """ Bifur gaussian

    """

    def __init__(self,
                 observable,
                 mean=Var(lwb=-1, upb=1),
                 sigmaL=Var(lwb=0, upb=1),
                 sigmaR=Var(lwb=0, upb=1),
                 name='BifurGauss', **kwds):

        super(BifurGauss, self).__init__(name=name, **kwds)

        roo_observable = self._add_observable(observable)

        roo_mean = self._add_parameter(mean, "mean")
        roo_sigmaL = self._add_parameter(sigmaL, "sigmaL")
        roo_sigmaR = self._add_parameter(sigmaR, "sigmaR")

        name = self.name
        title = 'RooBifurGauss PDF'

        self.roo_pdf = ROOT.RooBifurGauss(name, title, roo_observable, roo_mean, roo_sigmaL, roo_sigmaR)


class BreitWigner(PDF):
    """ Standard gaussian

    """
    def __init__(self,
                 observable,
                 mean=Var(lwb=-1, upb=1),
                 sigma=Var(lwb=0, upb=1),
                 name='BreitWigner', **kwds):

        super(BreitWigner, self).__init__(name=name, **kwds)

        roo_observable = self._add_observable(observable)

        roo_mean = self._add_parameter(mean, name="mean")
        roo_sigma = self._add_parameter(sigma, name="sigma")

        name = self.name
        title = 'BreitWigner PDF'

        self.roo_pdf = ROOT.RooBreitWigner(name, title, roo_observable, roo_mean, roo_sigma)


class Argus(PDF):
    """ Argus PDF

    """
    def __init__(self,
                 observable=Var('mbc'),
                 m0=Var("argus_m0", val=5.2889, lwb=5.288, upb=5.289),
                 c=Var("argus_c", val=-50, lwb=-1000, upb=1),
                 name="argus",
                 **kwds):
        self.initial_m0 = m0
        self.initial_c = c

        super(Argus, self).__init__(name=name, observables=[observable], **kwds)

    def init_pdf(self):
        roo_observable = self.get_observable()
        roo_argus_m0 = self._add_parameter(self.initial_m0, name="%s_m0"%self.name)
        roo_argus_c = self._add_parameter(self.initial_c, name="%s_c"%self.name)

        name = self.name
        title = "Argus"

        self.roo_pdf = ROOT.RooArgusBG(name, title, roo_observable, roo_argus_m0, roo_argus_c)
        self.roo_pdf.Print()


class CrystalBall(PDF):
    """ Crystal Ball PDF

        Args:
            observable (str) or (RooRealVar): observable for the pdf
        """
    def __init__(self,
                 observable='mbc',
                 mean=Var("cb_mean", val=5.2794, lwb=5.276, upb=5.29),
                 sigma=Var("cb_sigma", val=0.00259, lwb=0.0012, upb=0.004),
                 alpha=Var("cb_alpha", val=2.45104, lwb=0.5, upb=5),
                 n=Var("cb_n", val=1.907, lwb=1.0, upb=20.0),
                 name="cb",
                 **kwds):

        self.initial_mean = mean
        self.initial_sigma = sigma
        self.initial_alpha = alpha
        self.initial_n = n

        super(CrystalBall, self).__init__(name=name, observables=[observable], **kwds)

    def init_pdf(self):
        roo_observable = self.get_observable()

        roo_cb_mean = self._add_parameter(self.initial_mean, name="%s_mean"%self.name)
        roo_cb_sigma = self._add_parameter(self.initial_sigma, name="%s_sigma"%self.name)
        roo_cb_alpha = self._add_parameter(self.initial_alpha, name="%s_alpha"%self.name)
        roo_cb_n = self._add_parameter(self.initial_n, name="%s_n"%self.name)

        name = self.name
        title = "CB Shape"

        self.roo_pdf = ROOT.RooCBShape(name, title, roo_observable,
                                       roo_cb_mean, roo_cb_sigma, roo_cb_alpha, roo_cb_n)


class Mbc(AddPdf):
    """ Mbc PDF

        This pdf is predefined as Argus for the background and CB shape for the signal.
        The shape parameters can be set to fitted parameters.

        It can also integrate the argus function over the signal region to estimate the
        number of background candidates there.

    """
    def __init__(self, observable=Var("mbc", lwb=5.22, upb=5.3), name='mbc_model', mc_shape=True, **kwds):
        argus_bkg_pdf = Argus(observable, name="bkg")
        cb_sig_pdf = CrystalBall(observable, name="cb")
        super(Mbc, self).__init__(pdfs=[ cb_sig_pdf, argus_bkg_pdf], name=name, **kwds)
        if mc_shape:
            self.set_data_shape()

    def set_data_shape(self):
        self.params['cb_mean'].setVal(5.27950857339)
        self.params['cb_sigma'].setVal(0.00257244992496)
        self.params['cb_alpha'].setVal(2.6510288204)
        self.params['cb_n'].setVal(1.15959232008)
        self.pdfs['cb'].fix(True)

    def set_mc_shape(self):
        self.params['cb_mean'].setVal(5.27950857339)
        self.params['cb_sigma'].setVal(0.00257244992496)
        self.params['cb_alpha'].setVal(2.6510288204)
        self.params['cb_n'].setVal(1.15959232008)
        self.pdfs['sig'].fix(True)

    def get_argus_integral(self, lwb, upb):
        for roo_observable in self.observables.values(): pass
        roo_observable = self.get_observable()
        roo_observable.setRange("intrange", lwb, upb)
        integral = self.pdfs['bkg']().analyticalIntegral(1, 'intrange')
        return integral

    def argus_norm_integral(self, min, max, norm_min=5.22, norm_max=5.3):
        norm = self.get_argus_integral(norm_min, norm_max)
        if norm == 0:
            return 0
        return self.get_argus_integral(min, max)/norm

    def get_nb_sigreg(self):
        return self.norms['bkg'].getVal() * self.argus_norm_integral(5.27, 5.3)


class Chebychev(PDF):
    """ Chebychev polynomial pdf

        This is a generic polynomial PDF

    """
    def __init__(self, observable, n=3, name='chebychev_bkg', **kwds):
        """
        Args:
            observable (str) or (RooRealVar) or (list): Observable for the pdf
            n (int): Degree of the polynomial
            name (Optional[str]): name of the pdf
        """
        self.n = n
        super(Chebychev, self).__init__(name=name, observables=[observable], **kwds)

        self.use_extended = False

    def init_pdf(self):
        roo_observable = self.get_observable()

        arglist_params = ROOT.RooArgList()
        for i in range(self.n):
            param_name = "{name}_{i}".format(name=self.name, i=i)
            param_title = "a{i}".format(i=i)

            param_var= Var(param_name, title=param_title, lwb=-1, upb=1, val=0.1)
            roo_param = self._add_parameter(param_var)
            arglist_params.add(roo_param)

        name = self.name
        title = "Chebychev"

        self.roo_pdf = ROOT.RooChebychev(name, title, roo_observable, arglist_params)


class ChebychevProd(ProdPdf):
    def __init__(self, observables, n=3, name="Chebychev_bkg", **kwds):
        """Product of polynomials in the observable dimensions
        """
        pdfs = []
        for observable in observables:
            if isinstance(observables, dict):
                observable = observables[observable]
            roo_variable = create_roo_variable(observable)
            chebychev_bkg_factor = Chebychev(observable, n=n, name=name + roo_variable.GetName())
            pdfs.append(chebychev_bkg_factor)

        super(ChebychevProd, self).__init__(pdfs=pdfs, name=name, **kwds)


class KernelDensity(PDF):
    def __init__(self, observable, data=None, weights=None, name='kde_bkg', description='', **kwds):
        self.description = description
        self.data = data  # if isinstance(data, ROOT.RooDataSet) else self.get_fit_data(data, weights)

        super(KernelDensity, self).__init__(name=name, observables=[observable], **kwds)

    def init_pdf(self):
        if self.data is not None:
            self.fit(self.data)

    def _fit(self, data_roo):
        self.roo_pdf = ROOT.RooKeysPdf(self.name,
                                       self.description,
                                       self.get_observable(),
                                       data_roo,
                                       ROOT.RooKeysPdf.MirrorBoth)


class KernelDensityProd(ProdPdf):
    def __init__(self, observables, data=None, weights=None, name=None, **kwds):
        name = 'bkg' if name is None else name
        #print("fucking Hell")
        pdfs = {}
        super(KernelDensityProd, self).__init__(pdfs=pdfs, name=name, **kwds)
        for o in observables:
            self._add_observable(observables[o])
            # roo_observable = create_roo_variable(observable)
            # observable_name = roo_observable.GetName()
            # kernel_density_factor = KernelDensity(observable, data, weights, name=name+observable_name)
            # pdfs.append(kernel_density_factor)


        self.has_data = False
        if data is not None:
            self.last_data = self.get_fit_data(data, weights=weights)
        else:
            self.has_data = True

    def _fit(self, data_roo):
        self.debug("Fitting all pfds")
        pdfs = {}
        for observable in self.observables:
            kernel_density_factor = KernelDensity(self.observables[observable], name=self.name + observable )
            kernel_density_factor.fit(data_roo)
            pdfs[self.name + observable] = kernel_density_factor
        self.pdfs = pdfs
        self.init_pdf()


class Afb(PDF):
    """ Forward backward asymmetry Pdf

    """
    def __init__(self,
                 observable,
                 FL=Var("FL", val=0.4, lwb=0, upb=1),
                 AFB=Var("AFB", val=0.13, lwb=-1, upb=2),
                 name='afb_model',
                 **kwds):
        """

        Args:
            observable (str) or (RooRealVar) or (list): Observable for the pdf
            FL (Optional[RooRealVar]): Optional override for the FL measure
                Can be used for simultaneous fitting
        """
        self.initial_FL = FL
        self.initial_AFB = AFB

        super(Afb, self).__init__(name=name, observables=[observable], **kwds)

    def init_pdf(self):
        roo_observable = self.get_observable()

        roo_afb = self._add_parameter(self.initial_AFB, name="AFB")
        roo_fl = self._add_parameter(self.initial_FL, name="FL")

        observable_name = roo_observable.GetName()
        fl_name = roo_fl.GetName()
        afb_name = roo_afb.GetName()

        p2_formula = "(2/3.)*({AFB}/(1.-{FL}))".format(AFB=afb_name, FL=fl_name)
        self.P2 = ROOT.RooFormulaVar('P2', 'P2', p2_formula, ROOT.RooArgList(roo_afb, roo_fl))
        self._add_parameter(self.P2, name="P2")



        formula_template = "(3/4.0)*{FL}*(1-{x}*{x})+(3/8.)*(1-{FL})*(1+{x}*{x})+{AFB}*{x}"
        formula = formula_template.format(x=observable_name, FL=fl_name, AFB=afb_name)

        arglist_params = ROOT.RooArgList(roo_observable, roo_fl, roo_afb)

        self.roo_pdf = ROOT.RooGenericPdf(self.name, formula, arglist_params)


class Fl(PDF):
    """ Forward backward asymmetry Pdf

    """
    def __init__(self,
                 observable,
                 FL=Var("FL", val=0.4, lwb=0, upb=1),
                 name='fl_model',
                 **kwds):
        """

        Args:
            observable (str) or (RooRealVar) or (list): Observable for the pdf
            FL (Optional[RooRealVar]): Optional override for the FL measure
                Can be used for simultaneous fitting
        """
        self.initial_FL = FL
        super(Fl, self).__init__(name=name, observables=[observable], **kwds)

    def init_pdf(self):
        roo_observable = self.get_observable()

        roo_fl = self._add_parameter(self.initial_FL,)

        observable_name = roo_observable.GetName()
        fl_name = roo_fl.GetName()

        formula_template = "(3/2.0)*{FL}*({x}*{x})+(3/4.0)*(1-{FL})*(1-{x}*{x})"
        formula = formula_template.format(x=observable_name, FL=fl_name)

        arglist_params = ROOT.RooArgList(roo_observable, roo_fl,)

        self.roo_pdf = ROOT.RooGenericPdf(self.name, formula, arglist_params)


class At(PDF):
    """ Forward backward asymmetry Pdf

    """

    def __init__(self,
                 observable,
                 AT=Var("AT", val=0.0, lwb=-10, upb=10),
                 AI=Var("AI", val=0.0, lwb=-10, upb=10),
                 FL=Var("FL", val=0.4, lwb=0, upb=1),
                 name='At_model',
                 **kwds):
        """

        Args:
            observable (str) or (RooRealVar) or (list): Observable for the pdf
            FL (Optional[RooRealVar]): Optional override for the FL measure
                Can be used for simultaneous fitting
        """
        self.initial_AT = AT
        self.initial_AI = AI
        self.initial_FL = FL
        super(At, self).__init__(name=name, observables=[observable], **kwds)

    def init_pdf(self):
        roo_observable = self.get_observable()

        roo_at = self._add_parameter(self.initial_AT, )
        roo_ai = self._add_parameter(self.initial_AI, )
        roo_fl = self._add_parameter(self.initial_FL, )

        observable_name = roo_observable.GetName()
        at_name = roo_at.GetName()
        ai_name = roo_ai.GetName()
        fl_name = roo_fl.GetName()

        formula_template = "(1/(2.0*3.14159265359))*(1+0.5*(1-{FL})*{AT}*cos(2*{x})+{AI}*sin(2*{x}))"
        formula = formula_template.format(x=observable_name, AT=at_name, AI=ai_name, FL=fl_name)

        arglist_params = ROOT.RooArgList(roo_observable, roo_fl, roo_ai, roo_at)

        self.roo_pdf = ROOT.RooGenericPdf(self.name, formula, arglist_params)
