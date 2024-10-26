# setup.py

from setuptools import setup, find_packages

setup(
    name='make_drawio_erd',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas',
        # Include other dependencies
    ],
    author='Fred Trotter',
    author_email='fred.trotter@careset.com',
    description='A package to generate draw.io XML files with simple ERD table diagrams from various data sources.',
    url='https://github.com/careset/make_drawio_erd',
)