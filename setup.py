# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in tierslieux/__init__.py
from tierslieux import __version__ as version

setup(
	name='tierslieux',
	version=version,
	description='Site de démonstration pour les tiers lieux',
	author='Dokos SAS',
	author_email='hello@dokos.io',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
