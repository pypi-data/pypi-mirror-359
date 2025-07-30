from setuptools import setup, find_packages
from hackbyte.version import __version__

setup(
	name='hackbyte',
	version=f'{__version__}',
	author='Dx4Grey',
	description='Memory scan and edit in simple Python CLI style.',
	packages=find_packages(),
	install_requires=[],
	entry_points={
		'console_scripts': [
			'hackbyte = hackbyte.__main__:main',
		],
	},
	python_requires='>=3.6'
)
