from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in beansnseeds/__init__.py
from beansnseeds import __version__ as version

setup(
	name="beansnseeds",
	version=version,
	description="beansnseeds",
	author="sammish",
	author_email="sammish.thundiyil@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
