# -*- coding: utf-8 -*-
""" Simple fit to a gaussian distribution

In this example a fit is performed to a simple gaussion distribution.

Observables can be initialised by a list with the column name / variable name as first argument, followed
by the range and/or with the initial value and range:
x = ('x', -3, 3)
x = ('mass', -3, 0.02, 3)

Parameters are initialised with a tuple: sigma=(0,1) or again including a starting parameter: sigma=(0.01, 0, 1)
The order here is not important.

All parameters and observables can also be initialised by a ROOT.RooRealVar.

"""

from pyroofit.models import Gauss, Chebychev
import numpy as np
import pandas as pd
import ROOT


df = {'mass': np.append(np.random.random_sample(1000)*10 + 745, np.random.normal(750, 1, 1000))}
df = pd.DataFrame(df)

x = ROOT.RooRealVar('mass', 'M', 750, 745, 755, 'GeV')  # or x = ('mass', 745, 755)

pdf_sig = Gauss(x, mean=(745, 755), sigma=(0.1, 1, 2), title="Signal")
pdf_bkg = Chebychev(x, n=1, title="Background")

pdf = pdf_sig + pdf_bkg

pdf.fit(df)
pdf.plot('example_sig_bkg.pdf', legend=True)
pdf.get()
