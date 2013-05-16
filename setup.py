from setuptools import setup, find_packages

version = '0.1'

setup(
	name='ckanext-pat',
	version=version,
	description='Extension for customising CKAN Forms',
	long_description="""\
	""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='',
	author='Hyperborea',
	author_email='info@hyperborea.com',
	url='',
	license='',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
	namespace_packages=['ckanext', 'ckanext.pat'],
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points=\
	"""
	[ckan.plugins]
	pat=ckanext.pat.plugin:PatDatasetForm


    [paste.paster_command]
    pat=ckanext.pat.commands:PatCommand
	""",
)