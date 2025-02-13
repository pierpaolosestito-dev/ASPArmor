from setuptools import setup,find_packages

setup(
	name="my_shared_library",
	version="1.0.0",
	description="Libreria condivisa tra le CLI",
	packages = find_packages(),
	install_requires = [],
	classifiers = ["Programming Language :: Python :: 3","License :: OSI Approved :: MIT License"],

)
