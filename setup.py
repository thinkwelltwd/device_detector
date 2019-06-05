#!/usr/bin/env python3
import io
import os
import re
from setuptools import setup, find_packages


def get_version():
    with open('device_detector/__init__.py', 'r') as f:
        line = f.readline()
        match = re.match(r'__version__ = \'([\d\.]+)\'', line)

        if not match:
            raise ImportError("Can't read the version of device_detector")

        version = match.group(1)
        return version


here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

setup(
    name='device_detector',
    version=get_version(),
    description="Python3 port of matomo's Device Detector",
    long_description=long_description,
    long_description_content_type='text/markdown',
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
