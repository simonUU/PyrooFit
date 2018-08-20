# -*- coding: utf-8 -*-
""" Automatic combination of PDFs

This module handles the automatic combination of PDFs.
A combination can be a product or addition of two PDFs.

Also convolution is supported.


Todo:
    * This needs more work, just barely working
    * Move and refactor simultaneous fitting

"""

import ROOT

from .pdf import PDF
from .utilities import AttrDict, is_iterable
from .observables import create_roo_variable
from .plotting import fast_plot
from .data import df2roo


class AddPdf(PDF):
    """ Add PDF class, for generic addition of pdfs

    This is a wrapper for ROOT.RooAddPdf it combines two PDF classes into an new PDF normed by normalisation factors.
    It is the generic way to fit multiple components in a fit.

    Examples:
        Two models of clas ``PDF`` can easily combined automatically by calling:
        `` add_pdf = pdf1 + pdf2 ``

        If more than two models are to be combined:
        `` add_pdf = AddPdf([pdf1, pdf2, pdf3])

    Attributes:
        pdfs (AttrDict): dict of pdfs in the object
        norms (AttrDict): dict of normalisations


    Todo:
        * Allow for absolute and relative normalisations.

    """

    def __init__(self, pdfs=None, name=None, **kwds):
        """ Init of the AddPdf

        Args:
            pdfs (:obj:`list` of :obj:`PDF`, optional):
                List of PDFs to be combined into the ROOT.RooAddPdf
            name (:obj:`str`, optional):
                Name of the combined object, if not specified, generic name from composites is created
            **kwds:
                Keyword Args for the PDF class

        """

        self.pdfs = AttrDict()
        self.first_pdf = None  # remember which was passed first to identify signal in plotting

        if pdfs is not None:
            for pdf in pdfs:
                if self.first_pdf is None:
                    self.first_pdf = pdf.name
                self.pdfs[pdf.name] = pdf

            if name is None:
                name = "_plus_".join(pdf.name for pdf in pdfs)
        else:
            if name is None:
                name = "AddPdf"

        self.norms = AttrDict()

        #: dict: external normalisations
        self._external_norms = {}

        super(AddPdf, self).__init__(name=name, **kwds)

        self.use_extended = True

    def constrain_norm(self, pdf, normalization):
        """ Constrain a norm with an external normalisation

        Args:
            pdf (:obj:`PDF` or :obj:`str`): PDF object from the AddPdf or name of corresponding PDF
            normalization (:obj:`ROOT.RooAbsReal`): New normalisation to be used in the ROOT.RooAddPdf initialisation

        """
        assert isinstance(pdf, PDF) or isinstance(pdf, str), "please specify pdf"
        if isinstance(pdf, PDF):
            pdf = pdf.name
        assert pdf in self.pdfs, "Pdf not found"

        # assert isinstance(normalization, ROOT.RooAbsReal), "Please provide ROOT.RooAbsReal type as normalisation"

        self._external_norms[pdf] = normalization
        self.init_pdf()  # reset the pdf and change corresponding normalisation

    def fix_norm(self, pdf, n=None, set_error=False):
        """ Fix the normalisation to a specified value

        Args:
            pdf (:obj:`PDF`): PDF object of the AddPdf
            n (:obj:`int`, optional): Fix to a specified normalisation value
            set_error (bool or float, optioal): Set the error of the normalisation

        """
        assert isinstance(pdf, PDF), "please specify pdf"
        assert pdf.name in self.pdfs, "Pdf not found"
        if n is not None:
            self.norms[pdf.name].setVal(n)
        if set_error:
            if isinstance(set_error, bool):
                self.norms[pdf.name].setError(n**0.5)
            else:
                self.norms[pdf.name].setError(set_error)
        self.norms[pdf.name].setConstant(True)

    def add(self, pdf, name=None):
        """ Add a pdf to the AddPdf

        Args:
            pdf (:obj:`PDF`): PDF object to be added
            name (:obj:`str`, optional): Name of the object within the AddPdf

        """
        if name is None:
            name = pdf.name
        else:
            pdf.name = name
        if self.first_pdf is None:
            self.first_pdf = pdf.name
        self.pdfs[name] = pdf
        self.init_pdf()

    def init_pdf(self):
        """ Initialise the AddPdf

        In this function the initialization of the ROOT.RooAddPdf happens and the handling of the normalisations is
        performed.

        """

        # Discard old normalisations, observables and params
        # but hold on to at least one reference to avoid deletion
        old_norms = self.norms
        old_observables = self.observables
        old_params = self.parameters

        # only reset observables if not already set
        # >> the user could change them intentionally
        if self.norms is None:
            self.norms = AttrDict()
            self.observables = AttrDict()
            self.parameters = AttrDict()

        argset_norm = ROOT.RooArgList()
        argset_roo_pdf = ROOT.RooArgList()

        for pdf_name, pdf in self.pdfs.items():
            if pdf_name not in self._external_norms:
                norm_var = ('n_'+pdf_name, 10, 0, 100000000)  # This is dangerous
                roo_norm = create_roo_variable(norm_var)
            else:
                roo_norm = self._external_norms[pdf_name]
            self.norms[pdf_name] = roo_norm
            self.parameters['n_' + pdf_name] = roo_norm
            argset_norm.add(roo_norm)
            argset_roo_pdf.add(pdf.roo_pdf)

            self.observables.update(pdf.observables)
            self.parameters.update(pdf.parameters)
        #self.params.update(self.norms)

        name = self.name
        title = self.name
        self.roo_pdf = ROOT.RooAddPdf(name, title, argset_roo_pdf, argset_norm)

    def _plot(self, filename, observable, data=None, components=True, *args, **kwargs):
        """ overwrite of PDF plot function

        This function is not to be used by user.

        """

        if data is None:
            data = self.last_data

        if components is True:
            components = [c for c in self.pdfs]

        if components is False:
            components = []

        if components:
            add_components = []
            for pdf_name, pdf in self.pdfs.items():
                if not pdf_name in components:
                    continue
                sig_norm = self.norms[pdf_name]
                add_components.append((pdf.roo_pdf, sig_norm.getVal()))
            components = add_components

        fast_plot(self.roo_pdf, data, observable, filename, components=components, *args, **kwargs)


class ProdPdf(PDF):
    """ Add PDF class, for generic product of pdfs

    This is a wrapper of ROOT.RooProdPdf, generic product of two PDFs

    """
    def __init__(self, pdfs, name=None, **kwds):
        """ Init of the ProdPdf

        Args:
            pdfs (:obj:`list` of :obj:`PDF`, optional):
                List of PDFs to be combined into the ROOT.RooAddPdf
            name (:obj:`str`, optional):
                Name of the combined object, if not specified, generic name from composites is created
            **kwds:
                Keyword Args for the PDF class

        """
        self.pdfs = AttrDict()

        for pdf in pdfs:
            self.pdfs[pdf.name] = pdf

        if name is None:
            name = "_plus_".join(pdf.name for pdf in pdfs)

        super(ProdPdf, self).__init__(name=name, **kwds)
        self.use_extended = False

    def add(self, pdf, name=None):
        """ Add a pdf to the ProdPdf

        Args:
            pdf (:obj:`PDF`): PDF object to be added
            name (:obj:`str`, optional): Name of the object within the AddPdf

        """
        if name is None:
            name = pdf.name
        self.pdfs[name] = pdf
        self.init_pdf()

    def init_pdf(self):
        """ Initialise the ProdPdf

        In this function the initialization of the ROOT.RooProdPdf happens.

        """
        # Discard old observables and params
        # but hold on to at least one reference to avoid deletion
        old_observables = self.observables
        old_params = self.parameters

        self.observables = AttrDict()
        self.parameters = AttrDict()

        argset_roo_pdf = ROOT.RooArgList()

        for pdf_name, pdf in self.pdfs.items():

            self.observables.update(pdf.observables)
            self.parameters.update(pdf.parameters)

            if pdf.roo_pdf is None:
                self.warn("Pdf is None")
                continue

            argset_roo_pdf.add(pdf.roo_pdf)

        name = self.name
        title = self.name
        self.roo_pdf = ROOT.RooProdPdf(name, title, argset_roo_pdf)


class Convolution(PDF):
    """ Convolutes two different pdfs

    """
    def __init__(self, pdf1, pdf2, name="RooFFTConvPdf", desc='', fft=False, **kwds):
        """
        Args:
            pdf1:
            pdf2:
        """
        self.pdf1 = pdf1
        self.pdf2 = pdf2
        self.desc = desc
        super(Convolution, self).__init__(name=name, **kwds)

        self.observables = AttrDict()
        self.parameters = AttrDict()

        self.observables.update(self.pdf1.observables)
        self.observables.update(self.pdf2.observables)

        self.parameters.update(self.pdf1.parameters)
        self.parameters.update(self.pdf2.parameters)

        if len(self.observables) != 1:
            raise NotImplemented("Currently support one dimensional convolutions")

        name = self.name
        title = self.title

        roo_observable = self.get_observable()

        roo_pdf1 = self.pdf1.roo_pdf
        roo_pdf2 = self.pdf2.roo_pdf
        if fft:
            self.roo_pdf = ROOT.RooFFTConvPdf(name, title, roo_observable, roo_pdf1, roo_pdf2)
        else:
            self.roo_pdf = ROOT.RooNumConvPdf(name, title, roo_observable, roo_pdf1, roo_pdf2)


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
            self.parameters.update(pdf.parameters)

        self.roo_pdf = ROOT.RooSimultaneous("simPdf", "simultaneous pdf", self.sample)

        for pdf, name in zip(self.sim_pdfs, self.pdf_names):
            self.roo_pdf.addPdf(pdf.roo_pdf, name)

    def get_fit_data(self, df, weights=None, observables=None, nbins=None):
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

                    roo_data = df2roo(data, observables=observables, weights=weights, bins=nbins)
                    data_sets.append(roo_data)
                    imports.append(ROOT.RooFit.Import(name, roo_data))
        else:
            # Get the data for each pdf
            for pdf, name in zip(self.sim_pdfs, self.pdf_names):
                observables = pdf.observables
                all_observables.update(observables)

                roo_data = df2roo(df, observables=observables, weights=weights, nbins=nbins)
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
