#!/usr/bin/env python

import sys, glob
from distutils.core import setup

DESCRIPTION = (
    'A set of utilies for pythonocc'
    )


CLASSIFIERS = [
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'License :: OSI Approved :: LGPL License',
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development'
    ]

setup(
    name = 'OCCUtils',
    version = '0.1-dev',
    author = 'Jelle Feringa',
    author_email = 'jferinga@gmail.com',
    url = 'https://github.com/tpaviot/pythonocc-utils',
    description = DESCRIPTION,
    long_description = open('README.md').read(),
    license = 'LGPLv3',
    platforms = 'Platform Independent',
    packages = ['OCCUtils'],
    keywords = 'pythonocc CAD',
    classifiers = CLASSIFIERS,
    requires = ['OCC'],
    package_data = { 'OCCUtils': ['README.md', 'doc/*.*', 'examples/*.*'], },
    )
