#!/usr/bin/env python3

from setuptools import setup
from tidal_chrome import version, description, requires
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    README = f.read()

setup(
    name='tidal-chrome',
    version=version,
    packages=['tidal_chrome'],
    url='https://github.com/SERVCUBED/tidal-chrome',
    license='AGPL',
    author='SERVCUBED',
    author_email='ben@servc.eu',
    description=description,
    long_description=README,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'tidal-chrome=tidal_chrome.cli:run',
        ],
    },
    data_files=[
        ('share/applications', ['tidal-google-chrome.desktop']),
    ],
)
