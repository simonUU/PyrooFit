PyrooFit
========

PyrooFit is a fit framework for python and pandas DataFrames on top of the ROOT.RooFit package.

The package allows for simple fits of standard PDFs and easy setup of custom PDFs in one or more fit dimensions.

Example
-------

Simple fit and plot of a Gaussian Distribution:

```sh
from pytoofit.models import Gauss
import numpy as np

data = np.random.normal(0, 1, 1000)

x = ['x', -3, 3]

pdf = Gauss(x, mean=[-1,1])
pdf.fit(data)
pdf.plot('example.pdf')
pdf.get()

```

A more complex example on combination of Gauss pdf for signal and Polynomial for background:

```sh
import pyroofit
from pytoofit.models import Gauss, Chebychev
import numpy as np
import pandas as pd
d = {}
d['mass'] = np.append(np.random.random_sample(1000)*6 -3,
                      np.random.normal(0, 1, 1000))
df = pd.DataFrame(df)


x = ROOT.RooRealVar('mass','M', 0, -3, 3,'GeV')

pdf_sig = Gauss(x, mean=[-1,1])
pdf_bkg = Chebychev(x,n=1)

pdf = pdf_sig + pdf_bkg

pdf.fit(df)
pdf.plot('example2.pdf')
pdf.get()

```

Installation
============

Dependencies: ROOT (with PyRoot enabled)


* Download this repository

* (recommended) Use or install anaconda python environment

* Activate ROOT installation with python support

* run ``python setup.py develop`` in this folder

* run ``python setup.py docs`` to create the documentation



Note
====

This project has been set up using PyScaffold 2.5.6. For details and usage
information on PyScaffold see http://pyscaffold.readthedocs.org/.


