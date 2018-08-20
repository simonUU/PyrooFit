# -*- coding: utf-8 -*-
""" Fit models predefined

This module contains predefined wrappers for ROOT.RooFit pdfs.

"""

import ROOT

from .pdf import PDF
from .composites import AddPdf, ProdPdf
from .observables import create_roo_variable


class Gauss(PDF):
    """ Standard gaussian

    """
    def __init__(self,
                 observable,
                 mean=(-1, 0, 1),
                 sigma=(0, 1),
                 name='gauss', **kwds):

        super(Gauss, self).__init__(name=name,  **kwds)

        x = self.add_observable(observable)

        mean = self.add_parameter(mean, "mean")
        sigma = self.add_parameter(sigma, "sigma")

        self.roo_pdf = ROOT.RooGaussian(self.name, self.title, x, mean, sigma)


class BifurGauss(PDF):
    """ Bifurcated gaussian

    """

    def __init__(self,
                 observable,
                 mean=(-1, 0, 1),
                 sigma_left=(0, 1),
                 sigma_right=(0, 1),
                 name='bigauss', **kwds):

        super(BifurGauss, self).__init__(name=name, **kwds)

        x = self.add_observable(observable)

        mean = self.add_parameter(mean, "mean")
        sigma_left = self.add_parameter(sigma_left, "sigma_left")
        sigma_right = self.add_parameter(sigma_right, "sigma_right")

        self.roo_pdf = ROOT.RooBifurGauss(self.name, self.title, x, mean, sigma_left, sigma_right)


class Exponential(PDF):
    """ Exponential pdf

    """
    def __init__(self,
                 observable,
                 c=(0, 1),
                 name="exponential", **kwds):

        super(Exponential, self).__init__(name=name, **kwds)

        x = self.add_observable(observable)

        c = self.add_parameter(c, "c")

        self.roo_pdf = ROOT.RooExponential(self.name, self.title, x, c)


class Landau(PDF):
    """ Landau PDF

    """
    def __init__(self,
                 observable,
                 mean=(0, 1),
                 sigma=(0, 1),
                 name="Landau", **kwds):

        super(Landau, self).__init__(name=name, **kwds)

        x = self.add_observable(observable)

        mean = self.add_parameter(mean, "mean")
        sigma = self.add_parameter(sigma, "sigma")

        self.roo_pdf = ROOT.RooLandau(self.name, self.title, x, mean, sigma)


class BreitWigner(PDF):
    """ BreitWigner PDF

    """
    def __init__(self,
                 observable,
                 mean=(-1, 0, 1),
                 sigma=(0, 1),
                 name='bw', **kwds):

        super(BreitWigner, self).__init__(name=name, **kwds)

        x = self.add_observable(observable)

        roo_mean = self.add_parameter(mean, "mean")
        roo_sigma = self.add_parameter(sigma, "sigma")

        self.roo_pdf = ROOT.RooBreitWigner(name, self.title, x, roo_mean, roo_sigma)


class Argus(PDF):
    """ Argus PDF with default values for B mesons at B factories

    """
    def __init__(self,
                 observable,
                 m0=(5.2889, 5.288, 5.289),
                 c=(-50, -1000, 1),
                 name="argus", **kwds):

        super(Argus, self).__init__(name=name, observables=[observable], **kwds)

        x = self.get_observable()

        m0 = self.add_parameter(m0, "m0")
        c = self.add_parameter(c, "c")

        self.roo_pdf = ROOT.RooArgusBG(self.name, self.title, x, m0, c)


class CrystalBall(PDF):
    """ Crystal Ball PDF with default values for B mesons at B factories

        """
    def __init__(self,
                 observable,
                 mean=(5.2794, 5.276, 5.29),
                 sigma=(0.00259, 0.0012, 0.004),
                 alpha=(2.45104, 0.5, 5),
                 n=(1.907, 1.0, 20.0),
                 name="cb", **kwds):

        super(CrystalBall, self).__init__(name=name, **kwds)

        x = self.add_observable(observable)

        mean = self.add_parameter(mean, "mean")
        sigma = self.add_parameter(sigma, "sigma")
        alpha = self.add_parameter(alpha, "alpha")
        n = self.add_parameter(n, "n")

        self.roo_pdf = ROOT.RooCBShape(self.name, self.title, x, mean, sigma, alpha, n)


class Mbc(AddPdf):
    """ Mbc PDF

    This pdf is predefined as Argus for the background and CB shape for the signal.
    The shape parameters can be set to fitted parameters.

    It can also integrate the argus function over the signal region to estimate the
    number of background candidates there.

    """
    def __init__(self,
                 observable=("mbc", 5.22, 5.3),
                 name='mbc', **kwds):

        argus_bkg_pdf = Argus(observable, name="argus")
        cb_sig_pdf = CrystalBall(observable, name="cb")
        super(Mbc, self).__init__(pdfs=[cb_sig_pdf, argus_bkg_pdf], name=name, **kwds)

    def get_argus_integral(self, lwb, upb):
        roo_observable = self.get_observable()
        roo_observable.setRange("intrange", lwb, upb)
        integral = self.pdfs['bkg']().analyticalIntegral(1, 'intrange')
        return integral

    def argus_norm_integral(self, lwb, upb, norm_min=5.22, norm_max=5.3):
        norm = self.get_argus_integral(norm_min, norm_max)
        if norm == 0:
            return 0
        return self.get_argus_integral(lwb, upb)/norm

    def get_nb_sigreg(self):
        return self.norms["argus"].getVal() * self.argus_norm_integral(5.27, 5.3)


class Chebychev(PDF):
    """ Chebychev polynomial pdf

        This is a generic polynomial PDF

    """
    def __init__(self,
                 observable,
                 n=3,
                 name='chebychev', **kwds):
        """
        Args:
            observable (str) or (RooRealVar) or (list): Observable for the pdf
            n (int): Degree of the polynomial
            name (Optional[str]): name of the pdf
        """
        self.n = n
        super(Chebychev, self).__init__(name=name, observables=[observable], **kwds)

        roo_observable = self.add_observable(observable)

        arglist_params = ROOT.RooArgList()
        for i in range(self.n):
            param_name = "{name}_{i}".format(name=self.name, i=i)

            param_var = (-1, 1, 0.1)
            roo_param = self.add_parameter(param_var, param_name)
            arglist_params.add(roo_param)

        self.roo_pdf = ROOT.RooChebychev(self.name, self.title, roo_observable, arglist_params)


class ChebychevProd(ProdPdf):
    def __init__(self,
                 observables,
                 n=3,
                 name="Chebychev_bkg", **kwds):
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
    """ Kernel Density estimator PDF

    """
    def __init__(self,
                 observable,
                 data=None,
                 mirror=True,
                 name='kde_bkg', **kwds):

        self.data = data  # if isinstance(data, ROOT.RooDataSet) else self.get_fit_data(data, weights)
        if isinstance(mirror, bool):
            self.use_mirror = ROOT.RooKeysPdf.NoMirror if not mirror else ROOT.RooKeysPdf.MirrorBoth
        else:
            self.use_mirror = mirror
        super(KernelDensity, self).__init__(name=name, observables=[observable], **kwds)

    def init_pdf(self):
        if self.data is not None:
            self.fit(self.data)

    def _fit(self, data_roo):
        self.roo_pdf = ROOT.RooKeysPdf(self.name,
                                       self.title,
                                       self.get_observable(),
                                       data_roo,
                                       self.use_mirror)


class KernelDensityProd(ProdPdf):
    def __init__(self, observables, data=None, weights=None, name=None, **kwds):
        name = 'bkg' if name is None else name
        pdfs = {}
        super(KernelDensityProd, self).__init__(pdfs=pdfs, name=name, **kwds)
        for o in observables:
            self.add_observable(observables[o])
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
            kernel_density_factor = KernelDensity(self.observables[observable], name=self.name + observable)
            kernel_density_factor.fit(data_roo)
            pdfs[self.name + observable] = kernel_density_factor
        self.pdfs = pdfs
        self.init_pdf()


class DstD0BG(PDF):
    """ ROOT.RooDstD0BG for D0-D* mass difference
    [ 1-exp{ (dm-dm0) / c} ] * (dm/dm0)**a + b*(dm/dm0 - 1)

    """
    def __init__(self,
                 observable,
                 dm0=(139.57, 155),
                 a=(0,  10),
                 b=(1, 5),
                 c=(1, 5),
                 name='DstD0BG', **kwds):

        super(DstD0BG, self).__init__(name=name, **kwds)

        x = self.add_observable(observable)

        dm0 = self.add_parameter(dm0, "dm0")
        a = self.add_parameter(a, "a")
        b = self.add_parameter(b, "b")
        c = self.add_parameter(c, "c")

        self.roo_pdf = ROOT.RooDstD0BG(self.name, self.title, x, dm0, a, b, c)
