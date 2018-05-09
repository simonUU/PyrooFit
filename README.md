PyrooFit
========

PyrooFit is a fit framework for python and pandas DataFrames on top of the ROOT.RooFit package.

The package allows for simple fits of standard PDFs and easy setup of custom PDFs in one or more fit dimensions.

Example
-------

Simple fit and plot of a Gaussian Distribution:

```python
from pyroofit.models import Gauss
import numpy as np

data = np.random.normal(0, 1, 1000)

pdf = Gauss(('x', -3, 3), mean=(-1, 0, 1))
pdf.fit(data)
pdf.plot('example_gauss.pdf',)

pdf.get()

```

A more complex example on combination of Gauss pdf for signal and Polynomial for background:

```python
from pyroofit.models import Gauss, Chebychev
import numpy as np
import pandas as pd
import ROOT


df = {'mass': np.append(np.random.random_sample(1000)*7 - 3.5, np.random.normal(0, 0.5, 1000))}
df = pd.DataFrame(df)

x = ROOT.RooRealVar('mass', 'M', 0, -3, 3, 'GeV')

pdf_sig = Gauss(x, mean=(-1, 1))
pdf_bkg = Chebychev(x, n=1)

pdf = pdf_sig + pdf_bkg

pdf.fit(df)
pdf.plot('example_sig_bkg.pdf')
pdf.get()

```

Observables can be initialised by a list or tuple with the column name / variable name as first argument, followed
by the range and/or with the initial value and range:
```
x = ('x', -3, 3)
x = ('mass', -3, 0.02, 3)
```

Parameters are initialised with a tuple: `sigma=(0,1)` 
or again including a starting parameter: `sigma=(0.01, 0, 1)`
The order here is not important.

All parameters and observables can also be initialised by a `ROOT.RooRealVar`.

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


