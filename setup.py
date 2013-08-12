from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(
	name='ckanext-tdt',
	version=version,
	description="A The DataTank extension for CKAN",
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Pieter Colpaert',
	author_email='pieter.colpaert@okfn.org',
	url='http://thedatatank.com',
	license='AGPLv3',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.tdt'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
        [ckan.plugins]
	# Add plugins here, eg
	tdt=ckanext.tdt.plugin:TDTPlugin
	""",
)
