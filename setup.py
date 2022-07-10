"""Pip installation script."""

import os
import re
from setuptools import find_packages, setup


def get_version():

    ver_file = 'matflow_cipher/_version.py'
    with open(ver_file) as handle:
        ver_str_line = handle.read()

    ver_pattern = r'^__version__ = [\'"]([^\'"]*)[\'"]'
    match = re.search(ver_pattern, ver_str_line, re.M)
    if match:
        ver_str = match.group(1)
    else:
        msg = 'Unable to find version string in "{}"'.format(ver_file)
        raise RuntimeError(msg)

    return ver_str

def get_long_description():
    readme_file = 'README.md'
    with open(readme_file, encoding='utf-8') as handle:
        contents = handle.read()
    return contents

setup(
    author="Adam J. Plowman",
    author_email='adam.plowman@manchester.ac.uk',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="MatFlow extension for the phase-field code CIPHER.",
    entry_points="""
        [matflow.extension]
        cipher=matflow_cipher
    """,
    install_requires=[
        'matflow',
        'hickle>=4.0.1',
    ],
    license="MIT license",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    keywords='matflow, materials-science, computational-workflow',
    name='matflow-cipher',
    packages=find_packages(),
    package_data={'': ['snippets/*.py']},
    project_urls={
        'GitHub': 'https://github.com/LightForm-group/matflow-cipher'
    },
    version=get_version(),
)
