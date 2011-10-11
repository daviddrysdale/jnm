#!/usr/bin/env python
"""
Tools for investigating Java class files and jar files.

Copyright (C) 2011 David Drysdale <dmd@lurklurk.org>
Copyright (C) 2004, 2005, 2006, 2011 Paul Boddie <paul@boddie.org.uk>
Copyright (C) 2010 Braden Thomas <bradenthomas@me.com>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU Lesser General Public License as published by the Free
Software Foundation; either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import distutils.core
import sys
# Importing setuptools adds some features like "setup.py test", but
# it's optional so swallow the error if it's not there.
try:
    import setuptools
except ImportError:
    pass

major, minor = sys.version_info[:2]
python_25 = (major > 2 or (major == 2 and minor >= 5))
if not python_25:
    raise RuntimeError("Python 2.5 or newer is required")

# Discover version from local code
from javaclass import __version__

distutils.core.setup(name='jnm',
                     version=__version__,
                     description="Tools for investigating Java class files and jar files",
                     author='David Drysdale',
                     author_email='dmd@lurklurk.org',
                     url='https://github.com/daviddrysdale/jnm',
                     license='GNU Lesser General Public License version 3 or later',
                     packages=['javaclass'],
                     scripts=['jnm', 'jldd', 'jdump', 'jdemangle'],
                     package_data={'java': ['java/FindJRE.class'],
                                   '': ['LICENSE', 'COPYING']},
                     platforms='Posix; MacOS X; Windows',
                     classifiers=['Development Status :: 3 - Alpha',
                                  'Intended Audience :: Developers',
                                  'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                                  'Operating System :: OS Independent',
                                  'Topic :: Software Development :: Disassemblers',
                                  ],
                     )

