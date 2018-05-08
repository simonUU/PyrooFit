# -*- coding: utf-8 -*-
""" Allowing simulataneous fitting.

"""


from .pdf import PDF
from .utilities import AttrDict, is_iterable
from .observables import Var, create_roo_variable
from .dirty.plotting import pull_plot2, pull_plot
from .data import df2roo

import ROOT


class AddPdf(PDF):
    """ Add PDF class, for generic addition of pdfs

    """
    def __init__(self, pdfs=None, name=None, norms=None, **kwds):

        self.pdfs = AttrDict()
        self.first_pdf = None  # remember which was passed first to identify signal in plotting

        if pdfs is not None:
            for pdf in pdfs:
                if self.first_pdf is None:
                    self.first_pdf = pdf.name
                self.pdfs[pdf.name] = pdf

        if name is None:
            name = "_plus_".join(pdf.name for pdf in pdfs)

        self.norms = AttrDict()
        self._external_norms={}  # To be used when there are external constraint norms
        super(AddPdf, self).__init__(name=name, **kwds)

        self.use_extended = True

    def constrain_norm(self, pdf, normalization):
        assert isinstance(pdf, PDF), "please specify pdf"
        assert pdf.name in self.pdfs, "Pdf not found"

        self._external_norms[pdf.name] = normalization
        self.init_pdf()

    def fix_norm(self, pdf, n, ):
        assert isinstance(pdf, PDF), "please specify pdf"
        assert pdf.name in self.pdfs, "Pdf not found"
        self.norms[pdf.name].setVal(n)
        self.norms[pdf.name].setError(n**0.5)
        self.norms[pdf.name].setConstant(True)

    def add(self, pdf, name=None):
        if name is None:
            name = pdf.name
        else:
            pdf.name = name
        if self.first_pdf is None:
            self.first_pdf = pdf.name
        self.pdfs[name] = pdf
        self.init_pdf()

    def init_pdf(self):
        # Discard old normalisations, observables and params
        # but hold on to at least one reference to avoid deletion
        old_norms = self.norms
        old_observables = self.observables
        old_params = self.params

        # only reset observables if not already set
        # >> the user could change them intentionally
        if self.norms is None:
            self.norms = AttrDict()
            self.observables = AttrDict()
            self.params = AttrDict()

        argset_norm = ROOT.RooArgList()
        argset_roo_pdf = ROOT.RooArgList()

        for pdf_name, pdf in self.pdfs.items():
            if pdf_name not in self._external_norms:
                norm_var = Var('n_'+pdf_name, val=10, lwb=0, upb=1000000)
                roo_norm = create_roo_variable(norm_var)
            else:
                roo_norm = self._external_norms[pdf_name]
            self.norms[pdf_name] = roo_norm
            self.params['n_'+pdf_name] = roo_norm
            argset_norm.add(roo_norm)
            argset_roo_pdf.add(pdf.roo_pdf)

            self.observables.update(pdf.observables)
            self.params.update(pdf.params)
        #self.params.update(self.norms)

        name = self.name
        title = self.name
        self.roo_pdf = ROOT.RooAddPdf(name, title, argset_roo_pdf, argset_norm)

    def _plot(self, filename, observable, data=None, *args, **kwargs):
        # pull_plot(self.pdf, self.last_data, observable, filename, *args, **kwargs)
        pdf_sig = None
        pdf_bkg = None
        if data is None:
            data = self.last_data
        components = []
        for pdf_name, pdf in self.pdfs.items():
            sig_norm = self.norms[pdf_name]
            components.append((pdf.roo_pdf, sig_norm.getVal()))
        pull_plot2(self.roo_pdf, data, observable, filename, components=components, *args, **kwargs)

    """
        def _plot(self, filename, observable, data=None, *args, **kwargs):
            #pull_plot(self.pdf, self.last_data, observable, filename, *args, **kwargs)
            pdf_sig = None
            pdf_bkg = None
            if data is None:
                data = self.last_data
                if self.first_pdf in pdf_name:
                    sig_norm = self.norms[pdf_name]
                    pdf_sig = (pdf.roo_pdf, sig_norm.getVal())
                else:
                    bkg_norm = self.norms[pdf_name]
                    pdf_bkg = (pdf.roo_pdf, bkg_norm.getVal())

            pull_plot(self.roo_pdf, data, observable, filename, pdf_sig=pdf_sig, pdf_bkg=pdf_bkg, *args, **kwargs)
    """


class ProdPdf(PDF):
    """ Add PDF class, for generic product of pdfs

    """
    def __init__(self, pdfs, name=None, **kwds):
        self.pdfs = AttrDict()

        for pdf in pdfs:
            self.pdfs[pdf.name] = pdf

        if name is None:
            name = "_plus_".join(pdf.name for pdf in pdfs)

        super(ProdPdf, self).__init__(name=name, **kwds)
        self.use_extended = False

    def add(self, pdf, name=None):
        if name is None:
            name = pdf.name
        self.pdfs[name] = pdf
        self.init_pdf()

    def init_pdf(self):
        # Discard old observables and params
        # but hold on to at least one reference to avoid deletion
        old_observables = self.observables
        old_params = self.params

        self.observables = AttrDict()
        self.params = AttrDict()

        argset_roo_pdf = ROOT.RooArgList()

        for pdf_name, pdf in self.pdfs.items():

            self.observables.update(pdf.observables)
            self.params.update(pdf.params)

            if pdf.roo_pdf is None:
                self.warn("Pdf is None")
                continue

            argset_roo_pdf.add(pdf.roo_pdf)

        name = self.name
        title = self.name
        self.roo_pdf = ROOT.RooProdPdf(name, name, argset_roo_pdf)


class Convolution(PDF):
    """ Convolutes two different pdfs

    """
    def __init__(self, pdf1, pdf2, name="RooFFTConvPdf", desc='', **kwds):
        """
        Args:
            pdf1:
            pdf2:
        """
        self.pdf1 = pdf1
        self.pdf2 = pdf2
        self.desc = desc
        super(Convolution, self).__init__(name="Convolution", **kwds)

    def init_pdf(self):
        old_observables = self.observables
        old_params = self.params
        self.observables = AttrDict()
        self.params = AttrDict()

        self.observables.update(self.pdf1.observables)
        self.observables.update(self.pdf2.observables)

        self.params.update(self.pdf1.params)
        self.params.update(self.pdf2.params)

        if len(self.observables) != 1:
            raise NotImplemented("Currently support one dimensional convolutions")

        name = self.name
        title = self.name

        roo_observable = self.get_observable()

        roo_pdf1 = self.pdf1.roo_pdf
        roo_pdf2 = self.pdf2.roo_pdf

        self.roo_pdf = ROOT.RooFFTConvPdf(name, title, roo_observable, roo_pdf1, roo_pdf2)


class SimFit(PDF):
    """
    """

    def __init__(self, *pdfs):
        super(SimFit, self).__init__(name='SimFit', )

        self.sim_pdfs = []
        self.pdf_names = []
        self.sample = ROOT.RooCategory('sample', 'sample')

        # Adding the passed pdfs
        for pdf in pdfs:
            # Catch if somebody passed a list
            if is_iterable(pdf):
                for p in pdf:
                    self.logger.warn('Pdfs appear as list')

            if not isinstance(pdf, PDF):
                self.logger.error("No pdf object")
                continue

            self.sim_pdfs.append(pdf)
            self.pdf_names.append(pdf.name)
            self.sample.defineType(pdf.name)
            self.observables.update(pdf.observables)
            self.params.update(pdf.params)

        self.roo_pdf = ROOT.RooSimultaneous("simPdf", "simultaneous pdf", self.sample)

        for pdf, name in zip(self.sim_pdfs, self.pdf_names):
            self.roo_pdf.addPdf(pdf.roo_pdf, name)

    def get_fit_data(self, df, weights=None, observables=None):
        """overwritten"""
        data_sets = []
        imports = []

        all_observables = {}

        if isinstance(df, list):
            # one dataset for each sim pdf
            for df_tuple in df:
                assert len(df_tuple) > 1, "at least one pdf for each data"
                pdfs = df_tuple[:-1]
                data = df_tuple[-1]

                for pdf in pdfs:
                    assert isinstance(pdf, PDF)
                    name = pdf.name
                    observables = pdf.observables
                    all_observables.update(observables)

                    roo_data = df2roo(data, observables=observables, weights=weights)
                    data_sets.append(roo_data)
                    imports.append(ROOT.RooFit.Import(name, roo_data))
        else:
            # Get the data for each pdf
            for pdf, name in zip(self.sim_pdfs, self.pdf_names):
                observables = pdf.observables
                all_observables.update(observables)

                roo_data = df2roo(df, observables=observables, weights=weights)
                data_sets.append(roo_data)
                imports.append(ROOT.RooFit.Import(name, roo_data))

        # Convert all observables
        observables_argset = ROOT.RooArgSet()
        for o in all_observables:
            observables_argset.add(all_observables[o])

        # Create the final dataset
        roo_dataset = ROOT.RooDataSet('combinedData', 'combined Data',
                                      observables_argset,
                                      ROOT.RooFit.Index(self.sample),
                                      *imports
                                      )
        return roo_dataset