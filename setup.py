from setuptools import setup, find_packages

setup(  name='dissectgen',
	author='vojtechsu',
	license='MIT',
	entry_points={"console_scripts":["dissectgen=dissectgen.dissectgen:main",
					 "dissectgen-merge=dissectgen.merge:main"]},
	packages=find_packages())
