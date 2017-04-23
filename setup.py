# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='shipper',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'bitarray',
        'click',
        'Pillow',
    ],
    entry_points='''
        [console_scripts]
        shipper=shipper.cli:cli
    '''
)
