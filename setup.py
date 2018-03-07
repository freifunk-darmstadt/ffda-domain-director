import codecs
import os.path

from pipenv.project import Project
from pipenv.utils import convert_deps_to_pip
from setuptools import setup, find_packages

with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'), encoding='utf-8') as h:
    long_description = h.read()

pipenv_file = Project(chdir=False).parsed_pipfile
requirements = convert_deps_to_pip(pipenv_file['packages'], r=False)

setup(
    name='domain-director',
    version='0.0.1',
    description='Director-server for Freifunk mesh-nodes to acquire their mesh-domain',
    long_description=long_description,
    author='David Bauer',
    author_email='david@darmstadt.freifunk.net',
    url='https://www.github.com/blocktrron/domain-director',
    license='AGPLv3',
    install_requires=requirements,
    packages=find_packages(),
    entry_points={
        'console_scripts': ['domain-director=domain_director:cli.run']
    },
)
