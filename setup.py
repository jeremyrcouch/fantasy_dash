from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(this_directory, 'LICENSE.txt'), encoding='utf-8') as f:
    license = f.read()

setup(
    name='fantasy_dashboard',
    version='0.0.1',
    description='Fantasy football dashboard.',
	long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jeremy Couch',
    author_email='jeremy.r.couch@gmail.com',
    url='https://github.com/jeremyrcouch/fantasy_dashboard',
    license=license,
    packages=find_packages(exclude=('tests'))
)

