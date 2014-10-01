#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name='SimpleStepper',
    version='0.1.0',
    description='Simprify your access to AWS resource.',
    author='ARASHI, Jumpei',
    author_email='jumpei.arashi@arashike.com',
    url='https://github.com/JumpeiArashi/SimpleStepper',
    license='MIT',
    install_requires=[
        'boto',
        'tornado',
    ],
    extras_require={
        'developer': ['tornado-cors']
    },
    tests_require=[
        'boto',
        'nose',
    ],
    classifiers=[
        'Programing Language :: Python :: 2.6',
        'Programing Language :: Python :: 2.7',
    ]
)
