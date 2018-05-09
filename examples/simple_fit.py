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

from pyroofit.models import Gauss
import numpy as np

data = np.random.normal(0, 1, 1000)

pdf = Gauss(('x', -3, 3), mean=(-1, 0, 1))
pdf.fit(data)
pdf.plot('example_gauss.pdf',)

pdf.get()
