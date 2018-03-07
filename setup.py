import codecs
import os.path

from setuptools import setup, find_packages

with codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.rst'), encoding='utf-8') as h:
    long_description = h.read()

setup(
    name='domain-director',
    version='0.0.2',
    description='Director-server for Freifunk mesh-nodes to acquire their mesh-domain',
    long_description=long_description,
    author='David Bauer',
    author_email='david@darmstadt.freifunk.net',
    url='https://www.github.com/blocktrron/domain-director',
    license='AGPLv3',
    install_requires=[
        "click",
        "fastkml",
        "flask",
        "geojson",
        "pyyaml",
        "requests",
        "shapely",
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['domain-director=domain_director:cli.run']
    },
)
