from setuptools import setup
import logging
from tidal_chrome import __version__, __description__, requires, README


# check availability of runtime dependencies
def check_dependency(package, version):
    """Issue a warning if the package is not available."""
    try:
        import gi
        gi.require_version(package.rsplit('.')[-1], version)
        __import__(package)
    except ImportError as e:
        # caused by either of the imports, probably the first
        logging.warning("Missing runtime dependencies:\n\t" + str(e))
    except ValueError as e:
        # caused by the gi.require_version() statement
        logging.warning("Missing runtime dependencies:\n\t" + str(e))
    except RuntimeError as e:
        # caused by the final __import__() statement
logging.warning("Bad runtime dependency:\n\t" + str(e))

setup(
    name='tidal-chrome',
    version=__version__,
    packages=['tidal_chrome', 'tidal_chrome.tidal_chrome_driver'],
    url='',
    license='GPL',
    author='SERVCUBED',
    author_email='ben@servc.eu',
    description=__description__,
    long_description=README,
    depends=('chromedriver', 'google-chrome', 'selenium', 'flask', 'naked'),
    data_files=[('node-mpris', ['node-mpris/index.js', 'node-mpris,package.json'])],
    scripts=['node-install.sh'],
    install_requires=requires,
    entry_points={
        'console_scripts': [
            'tidal-chrome=tidal_chrome',
        ],
    },
)
