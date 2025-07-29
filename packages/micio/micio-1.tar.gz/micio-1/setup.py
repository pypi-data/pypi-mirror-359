"""  Created on 01/07/2025::
------------- setup.py -------------
"""

import setuptools
from micio.__about__ import (__title__, __author__, __version__)


setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    # description=__about__,
    license='MIT',
    long_description='mc',
    long_description_content_type="text/markdown",
    packages=['micio', 'micio.res'],
    package_data={'':  ['../micio/res/*']},
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent"],
    python_requires='>=3.6',
)


