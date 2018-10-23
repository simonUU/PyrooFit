# -*- coding: utf-8 -*-
""" Simple fit to a histogram template

In this example a template histogram is created from some data.
Then the template is fixed and fitted to some new data containing a different number of entries.
"""

from pyroofit.models import HistPDF
from pyroofit.composites import AddPdf
import numpy as np
# import ROOT

# First we build the template of some data
template_data = np.random.normal(0, 1, 1000)

pdf = HistPDF(
    ('x', -3, 3),
    template_data,
    nbins=10,
)
pdf.plot('example_hist.pdf')
pdf.fix()
pdf.get()

# And now we can fit that template to some new data to measure the yield
fit_data = np.random.normal(0, 1, 5000)

pdf2 = AddPdf([pdf])
pdf2.fit(fit_data)
# pdf2.plot('example_hist.pdf')  # Bug causes this to error atm
pdf2.get()
