# -*- coding: utf-8 -*-
""" Simple fit to a histogram template

In this example a template histogram is created from the given data

The number of bins must be specified
"""

from pyroofit.models import HistPDF
import numpy as np
# import ROOT

template_data = np.random.normal(0, 1, 1000)

pdf = HistPDF(
    ('x', -3, 3),
    template_data,
    nbins=10,
)
pdf.plot('example_hist.pdf')
pdf.get()
