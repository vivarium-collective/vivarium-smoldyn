import os
import glob
import setuptools
from distutils.core import setup

with open("README.md", 'r') as readme:
    long_description = readme.read()

setup(
    name='vivarium-smoldyn',
    version='0.0.1',
    packages=[
        'vivarium_smoldyn',
        'vivarium_smoldyn.processes',
        'vivarium_smoldyn.composites',
        'vivarium_smoldyn.experiments',
    ],
    author='Eran Agmon',
    author_email='eagmon@stanford.edu',
    url='https://github.com/vivarium-collective/vivarium-smoldyn',
    license='MIT',
    entry_points={
        'console_scripts': []},
    short_description='a vivarium wrapper for smoldyn',
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data={},
    include_package_data=True,
    install_requires=[
        'vivarium-core>=0.3.0',
        'smoldyn'
    ],
)
