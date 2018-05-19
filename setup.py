#!/usr/bin/env python3
import io
import os
from setuptools import setup, find_packages
import device_detector

here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='device_detector',
    version=device_detector.__version__,
    description="Python3 port of matomo's Device Detector",
    long_description=long_description,
    author='Dave Burkholder',
    author_email='dave@thinkwelldesigns.com',
    packages=find_packages(exclude=["tests"]),
    package_dir={'': '.'},
    license='MIT',
    zip_safe=True,
    url='https://github.com/thinkwelltwd/device_detector',
    include_package_data=True,
    package_data={
        '': ['*.yml'],
    },
    install_requires=['pyyaml'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
)
