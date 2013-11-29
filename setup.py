#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup
from distutils.command.build_scripts import build_scripts


class BuildScripts(build_scripts):
    """Build the package."""
    def run(self):
        """Run building."""
        # These lines remove the .py extension from executables
        self.mkpath(self.build_dir)
        for script in self.scripts:
            root, _ = os.path.splitext(script)
            self.copy_file(script, os.path.join(self.build_dir, root))

setup(
    name="wsreload",
    version='2.0',
    description="Reload browser tabs through websocket",
    author="Florian Mounier",
    author_email="paradoxxx.zero@gmail.com",
    packages=['wsreload'],
    scripts=['wsreload.py', 'wsreload-server.py'],
    cmdclass={"build_scripts": BuildScripts},
    platforms="Any",
    provides=['wsreload'],
    install_requires=['tornado', 'pyinotify'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3"])
