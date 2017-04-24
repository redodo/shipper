# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='shipper',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'bitarray==0.8.1',
        'click==6.7',
        'Pillow==4.1.0',
        'simple-crypt==4.1.7',
    ],
    entry_points='''
        [console_scripts]
        shipper=shipper.cli:cli
    '''
)
