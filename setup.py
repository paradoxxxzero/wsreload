#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup
from distutils.command.build_scripts import build_scripts


class BuildScripts(build_scripts):
    """Build the package."""
    def run(self):
        """Run building."""
        # These lines remove the .py extension from the radicale executable
        self.mkpath(self.build_dir)
        for script in self.scripts:
            root, _ = os.path.splitext(script)
            self.copy_file(script, os.path.join(self.build_dir, root))

setup(
    name="wsreload",
    version='1.1.1',
    description="Reload browser tabs through websocket",
    author="Florian Mounier",
    author_email="paradoxxx.zero@gmail.com",
    packages=['wsreload'],
    scripts=['wsreload.py', 'wsreload-server.py'],
    cmdclass={"build_scripts": BuildScripts},
    platforms="Any",
    provides=['wsreload'],
    install_requires=['ws4py', 'cherrypy', 'pyinotify'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2"])
