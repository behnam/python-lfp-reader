#!/usr/bin/env python

from distutils.core import setup

setup(name="lfp-reader", version="1.1",
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
            'lfp_file_info.py',
            'lfp_picture_info.py',
            'lfp_picture_viewer.py',
            'lfp_storage_extractor.py',
            ],

        data_files=[
            'COPYING.txt',
            'README.rst',
            ],

        install_requires=[
            "PIL",
            ],
        )

