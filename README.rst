H5 Validator - Validation tool for testing Fast5 files against the schema
===============================================================================

``ont_h5_validator`` is a simple tool for validating the structure of fast5 files
against the file schema maintained by Oxford Nanopore Technologies

- Source code: https://github.com/nanoporetech/ont_h5_validator

It provides:

- Command line validation tools for validating fast5 files
- Json format data schemas specifying the fast5 standard

**NB** The h5_validator is intended as a tool to validate the output of the
latest MinKNOW-core. The schemas are currently intended to be restrictive and
therefore additional fields (for example those added by albacore or guppy)
will not be expected in the schema and flagged as invalid.

Getting Started
===============================================================================
The ``ont_h5_validator`` is available on PyPI and can be installed via pip::

    pip install ont-h5-validator

Alternatively it is available on github where it can be built from source::

    git clone https://github.com/nanoporetech/ont_h5_validator
    cd ont_h5_validator
    python setup.py install

Dependencies
------------------------------------------------------------------------------
``ont_h5_validator`` is a pure python project and should run on most python
versions and operating systems.

It requires:

- `h5py <http://www.h5py.org>`_
- `NumPy <https://www.numpy.org>`_
- `PyYAML <https://pyyaml.org>`_: 3.1.1 or higher

Interface - Console Scripts
===============================================================================
The ``ont_h5_validator`` provides a console script for validating fast5 files
against a JSON schema. This script is added during installation of this
project and can be called from the command line or from within python.

h5_validate
-------------------------------------------------------------------------------
This script expects::

    h5_validate
        schema <(path) json schema file (see note-1)>
        filename <(path) fast5 file>
        [optional] -v, --verbose <(bool) show additional verbose output; default=False>
        [optional] --debug <(bool) include additional debug logging; default=False>

*note-1:* if the schema file is not found on the path specified the script will
additionally look in the default directory ``h5_validator/schemas/``

**example usage**::

    h5_validate multi_read_fast5.yaml /data/multi_read.fast5 -v
