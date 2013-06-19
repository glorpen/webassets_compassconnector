#!/usr/bin/env python

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

requires=['webassets']

setup(
    name='webassets_compassconnector',
    version="0.1",
    description='Complete Compass integration for Webassets',
    long_description=README,
    author='Arkadiusz Dzięgiel',
    author_email='arkadiusz.dziegiel@glorpen.pl',
    license='GPL-3',
    url='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requires,
    tests_require=requires,
    test_suite="webassets_cc",
)
