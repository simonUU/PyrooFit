# -*- coding: utf-8 -*-
""" Example of a simultaneous fit.

WARNING: this is experimental and the interface might change

"""

from pyroofit.models import Gauss, Chebychev
from pyroofit.composits import SimFit
import numpy as np
import pandas as pd
import ROOT


df_mixed = {'mass': np.append(np.random.random_sample(1000)*7 - 3.5, np.random.normal(0, 0.5, 1000))}
df_mixed = pd.DataFrame(df_mixed)

df_bkg = {'mass': np.random.random_sample(2000)*7 - 3.5}
df_bkg = pd.DataFrame(df_bkg)

x = ROOT.RooRealVar('mass', 'M', 0, -3, 3, 'GeV')

pdf_sig = Gauss(x, mean=(-1, 1))
pdf_bkg = Chebychev(x, n=1)

pdf = pdf_sig + pdf_bkg

sf = SimFit(pdf, pdf_bkg)
sf.use_extended = False  # bug
sf.use_minos = True
sf.fit([(pdf, df_mixed), (pdf_bkg, df_bkg)])

pdf_bkg.plot('example_simfit_bkg.pdf', df_bkg)
pdf.plot('example_simfit_combined.pdf',
         df_mixed,
         nbins=20,
         extra_info=[["Legend"], ["More Legend"], ['#mu', *pdf.get('mean')], ['#sigma', *pdf.get('sigma')]])
pdf.get()

