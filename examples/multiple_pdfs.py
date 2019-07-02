# -*- coding: utf-8 -*-
""" A fit to several pdfs using the AddPdf Class

"""

from pyroofit.models import Gauss, Chebychev
from pyroofit.composites import AddPdf
import numpy as np
import pandas as pd
import ROOT


dist_signal = np.append(np.random.normal(750, 1.5, 500), np.random.normal(750, .5, 1000))
dist_background = np.random.random_sample(1000)*10 + 745,
df = pd.DataFrame({'mass': np.append(dist_signal, dist_background)})


x = ROOT.RooRealVar('mass', 'M', 750, 745, 755, 'GeV')  # or x = ('mass', 745, 755)

pdf_sig1 = Gauss(x, mean=(745, 755), sigma=(0.1, 1, 2), name="Gauss1")
# We want to furthermore constrain the mean to be the same
pdf_sig2 = Gauss(x, mean=pdf_sig1.parameters.mean, sigma=(0.1, 1, 2), name="Gauss2")

pdf_bkg = Chebychev(x, n=1, name="bkg")

pdf = AddPdf([pdf_sig1, pdf_sig2, pdf_bkg], name="model")

pdf.fit(df)
pdf.plot('multiple_pdfs.pdf', legend=True)
pdf.get()
