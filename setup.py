import os
import re

from setuptools import setup, find_packages

__pkg_name__ = "h5_validator"
DESCRIPTION = u'Hdf5 validator package'
with open('README.rst') as readme:
    DOCUMENTATION = readme.read()

def get_version():
    init_path = os.path.join(__pkg_name__, '__init__.py')
    # This is ugly, but avoids importing project before setup gets dependencies
    # See https://packaging.python.org/guides/single-sourcing-package-version/
    with open(init_path, 'r') as init_fh:
        version_file = init_fh.read()
    vsre = r"^__version__ = ['\"]([^'\"]*)['\"]"
    version_match = re.search(vsre, version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string in: " + init_path)


setup(
    name="ont-" + __pkg_name__.replace("_", "-"),
    version=get_version(),
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
