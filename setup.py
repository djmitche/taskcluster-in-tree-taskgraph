from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='taskgraph',

    version='0.0.1',

    description='TaskCluster task graph generation',
    long_description=long_description,
    url='https://github.com/djmtiche/in-tree-taskgraph',
    author='Dustin J. Mitchell',
    author_email='dustin@mozilla.com',
    license='MPL2',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(exclude=['taskgraph']),
    install_requires=[
        'pyyaml',
        'pystache',
    ],

    extras_require={
        'test': ['nose'],
    },
)

