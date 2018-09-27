from paver.tasks import task, BuildFailure
from paver.easy import sh

@task
def tests():
    """Do the tests"""
    sh('green -r')

@task
def codeqa():
    """Run code quality check"""

    try:
        sh('flake8 h5_validator')
    except BuildFailure:
        pep8_fail = True
    else:
        pep8_fail = False

    try:
        sh("pydocstyle h5_validator")
    except BuildFailure:
        docstring_fail = True
    else:
        docstring_fail = False

    if pep8_fail or docstring_fail:
        raise BuildFailure('Code Quality checks failed')

@task
def docs():
    """Build the Sphinx documentation"""
    sh('sphinx-build -W -b html docs docs/_build/html')
