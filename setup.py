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
    url='https://github.com/freifunk-darmstadt/ffda-domain-director',
    license='AGPLv3',
    include_package_data=True,
    install_requires=[
        "click",
        "fastkml",
        "flask",
        "geojson",
        "mozls",
        "peewee",
        "pyyaml",
        "requests",
        "shapely",
        "pymeshviewer",
        "apscheduler",
        "waitress>=1.4.3",
        "slpp-23"
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'domain-director=director.cli:run',
            'domain-director-converter=kml_converter.cli:run',
            'domain-director-validator=validator.cli:run'
        ]
    },
)
