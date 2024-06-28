#!/usr/bin/env python3

# Copyright 2024 The Johns Hopkins University Applied Physics Laboratory LLC
# All rights reserved.
#
# Licensed under the 3-Clause BSD License (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://opensource.org/licenses/BSD-3-Clause
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
__author__ = 'Chace Ashcraft, Jared Markowitz, Aurora Schmidt'
__email__ = 'Chace.Ashcraft@jhuapl.edu, Jared.Markowitz@jhuapl.edu, Aurora.Schmidt@jhuapl.edu'
__version__ = '0.0.1'
install_requires = ['numpy>=1.26.4',
                    'gymnasium>=0.29.1',
                    'pygame>=2.5.2',
                    'requests',
                    ]

setuptools.setup(
    name='testbed4hat',
    version=__version__,
    description='TODO',
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url=,
    author=__author__,
    author_email=__email__,
    license='BSD 3-Clause',
    python_requires='>=3.11',
    packages=setuptools.find_packages(),
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Programming Language :: Python :: 3 :: Only',
    ],
    # keywords='todo',
    install_requires=install_requires,
    extras_require={},
    zip_safe=False
)
