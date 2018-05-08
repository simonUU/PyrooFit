#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from pyroofit.skeleton import fib

__author__ = "Simon Wehle"
__copyright__ = "Simon Wehle"
__license__ = "gpl3"


def test_fib():
    assert fib(1) == 1
    assert fib(2) == 1
    assert fib(7) == 13
    with pytest.raises(AssertionError):
        fib(-10)
