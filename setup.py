import os
from setuptools import setup, find_packages

from h5_validator import __version__

__pkg_name__ = "h5_validator"
DESCRIPTION = u'Hdf5 validator package'
with open('README.rst') as readme:
    DOCUMENTATION = readme.read()

init_path = os.path.join(__pkg_name__, '__init__.py')

setup(
    name=__pkg_name__.replace("_", "-"),
    version=__version__,
    url='https://nanoporetech.com',
    author='Oxford Nanopore Technologies Ltd',
    author_email='info@nanoporetech.com',
    description=DESCRIPTION,
    long_description=DOCUMENTATION,
    zip_safe=True,
    packages=find_packages(),
    install_requires=['numpy', 'h5py', 'PyYAML>=3.11'],
    package_data={__pkg_name__: ["schemas/*.yaml"]},
    entry_points={'console_scripts': [
        'h5_validate={}.cli:main'.format(__pkg_name__)
    ]},
)
