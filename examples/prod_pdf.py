# -*- coding: utf-8 -*-
""" Simple product pdf

"""

from pyroofit.models import Gauss
import numpy as np
import pandas as pd

# Creating some pseudo data
mean = (1, 2)
cov = [[1, -.1], [-.1, 1]]
x = np.random.multivariate_normal(mean, cov, 300)
df = pd.DataFrame({'x': x[:, 0], 'y': x[:, 1]})

# Initialize the PDF
pdf_x = Gauss(['x', -1, 5], mean=[0, 3], sigma=[0.1, 2], name='gx')
pdf_y = Gauss(['y', -1, 5], mean=[0, 3], sigma=pdf_x.parameters.sigma, name='gy')
pdf = pdf_x * pdf_y

# Fit
pdf.fit(df)
pdf.get()
