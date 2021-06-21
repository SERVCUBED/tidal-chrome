#!/usr/bin/env python3

from os import path
from setuptools import setup
from tidal_chrome import version, description, requires

with open(path.join(path.dirname(__file__), 'README.md')) as f:
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
    long_description_content_type='text/markdown',
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'tidal-chrome=tidal_chrome.cli:run',
        ],
    },
    data_files=[
        ('share/mime/packages', ['tidal-google-chrome.xml']),
        ('share/applications', ['tidal-google-chrome.desktop']),
    ],
)
