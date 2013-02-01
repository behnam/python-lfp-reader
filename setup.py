#!/usr/bin/env python
#
# lfp-reader
# LFP (Light Field Photography) File Reader.
#
# http://behnam.github.com/python-lfp-reader/
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
# Copyright (C) 2012  Behnam Esfahbod


from distutils.core import setup


setup(name="lfp-reader", version="1.4.6",
        description="LFP (Light Field Photography) File Reader",
        long_description=open('README.rst').read(),

        url='http://behnam.github.com/python-lfp-reader/',
        download_url='https://github.com/behnam/python-lfp-reader/',

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
        author_email="behnam@esfahbod.info",

        packages=[
            'lfp_reader'
            ],

        scripts=[
            'lfp_file_exporter.py',
            'lfp_file_info.py',
            'lfp_picture_all_focus.py',
            'lfp_picture_exporter.py',
            'lfp_picture_info.py',
            'lfp_picture_viewer.py',
            'lfp_storage_exporter.py',
            'lfp_storage_info.py',
            ],

        data_files=[
            ('lib/python-lfp-reader',
                ('COPYING.txt', 'README.rst')),
            ],

        install_requires=[
            "Pillow",
            ],
        )

