#!/usr/bin/env python
#
# lfp-reader
# LFP (Light Field Photography) File Reader.
#
# http://code.behnam.es/python-lfp-reader/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2012-2013  Behnam Esfahbod


from distutils.core import setup

release_version="2.0.0"

setup(name="lfp-reader", version=release_version,
        description="LFP (Light Field Photography) File Reader",
        long_description=open('README.rst').read(),

        url='http://behnam.github.com/python-lfp-reader/',
        download_url='https://github.com/behnam/python-lfp-reader/archive/python-lfp-reader-%s.zip' % release_version,

        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Natural Language :: English',
            'Programming Language :: Python',
            'Topic :: Multimedia :: Graphics',
            'Topic :: Multimedia :: Graphics :: Viewers',
            ],
        platforms=['any'],
        license="GNU General Public License v3 or later (GPLv3+)",

        author="Behnam Esfahbod",
        author_email="behnam@behnam.es",

        packages=[
            'lfp_reader'
            ],

        scripts=[
            'lfp-file.py',
            'lfp-picture.py',
            'lfp-storage.py',
            'lfp-viewer.py',
            ],

        data_files=[
            ('lib/python-lfp-reader',
                ('COPYING.txt', 'README.rst')),
            ],

        install_requires=[
            "Pillow",
            ],
        )

