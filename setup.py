#!/usr/bin/python3

from distutils.core import setup

setup(
    name="energymon-mvo",
    version="0.1",
    description="store smart energy meter data",
    author="Michael Vogt",
    author_email="michael.vogt@gmail.com",
    url="https://github.com/mvo5/energymon",
    packages=["energymon"],
    scripts=["bin/energymon"],
)
