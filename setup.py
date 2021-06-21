#!/usr/bin/env python3

from subprocess import Popen, PIPE, STDOUT
import sys
from os import path

from setuptools import setup
from setuptools.command.install import install

from tidal_chrome import version, description, requires

with open(path.join(path.dirname(__file__), 'README.md')) as f:
    README = f.read()


class Install(install):
    def run(self):
        install.run(self)
        if self._dry_run is not None:
            print("Skipping mime handler registration due to dry run.")
            return

        ucmds = {cmd[0]: cmd[1] for cmd in install.user_options}
        if "user" not in ucmds or ucmds["user"] is not None:
            # TODO change prefix
            return

        print("Registering mime type handlers...")
        from xdg import BaseDirectory
        mp = f'{self.prefix}/share/mime/' if self.user == 0 else BaseDirectory.save_data_path("mime")
        print(f'Attemtping to use mime directory: {mp}')
        if not path.isdir(mp):
            print("Path is not a valid directory. Aborting mime registration.")
            return
        print("Registering with native mimetype handlers...")
        with Popen(['/usr/bin/update-mime-database', mp], stdout=PIPE, stderr=STDOUT) as p:
            for l in p.stdout:
                print(f"\t{str(l)}")
            p.wait()
            print("Success!" if p.returncode == 0 else "Error whilst registering mime handler database.")
        print("Registering desktop entry with xdg-mime...")
        with Popen(['/usr/bin/xdg-mime', 'install', 'tidal-google-chrome.desktop'], stdout=PIPE, stderr=STDOUT) as p:
            for l in p.stdout:
                print(f"\t{str(l)}")
            p.wait()
            print("Success!" if p.returncode == 0 else "Error whilst registering with xdg-mime.")

        # from xdg import DesktopEntry, Mime
        # xdg.Mime.install_mime_info("tidal-google-chrome", "tidal-google-chrome.xml")
        # de = DesktopEntry(df)
        # mts = de.getMimeTypes()
        # M = Mime()
        # cmd = '/usr/bin/xdg-mime'
        #  if not path.exists(cmd):
        #     sys.stderr.write(f'Unable to find xdg-mime utility under "{cmd}" to register application. Install the '
        #                      'xdg-utils package and then re-run this installation.')
        # cmd = f"{cmd} install {df}"
        # from subprocess import call, SubprocessError
        # try:
        #     print("Registering mime type handler")
        #     call(cmd.split())
        # except SubprocessError:
        #     sys.stderr.write(f'Unable to register mime type with command "{cmd}"')


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
    # requires=requires,
    install_requires=['setuptools', 'wheel', 'xdg-mime', requires],
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
    cmdclass={
        'install': Install,
    },
)
