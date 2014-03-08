#!/usr/bin/env python

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

requires=['webassets']

setup(
    name='webassets_compassconnector',
    version="0.2.3",
    description='Complete Compass integration for Webassets',
    long_description=README,
    author='Arkadiusz Dzięgiel',
    author_email='arkadiusz.dziegiel@glorpen.pl',
    license='GPL-3',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=requires,
    tests_require=requires,
    test_suite="webassets_cc",
    url='https://bitbucket.org/glorpen/webassets_compassconnector',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
