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


