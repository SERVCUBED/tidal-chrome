from setuptools import setup
from tidal_chrome import __version__, __description__, requires
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    README = f.read()

setup(
    name='tidal-chrome',
    version=__version__,
    packages=['tidal_chrome'],
    url='https://github.com/SERVCUBED/tidal-chrome',
    license='AGPL',
    author='SERVCUBED',
    author_email='ben@servc.eu',
    description=__description__,
    long_description=README,
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'tidal-chrome=tidal_chrome.cli:run',
        ],
    },
)
