import os
import http.server

from invoke import task


TESTS_FILE = 'tests.py'
MODULE_NAME = 'logger_helper'
DOCS_DIR = 'docs'
CI_IMAGE = 'logger-helper-ci'

IN_CI_ENVIRONMENT = os.getenv('CI', None) is not None
BUILT_CI = False # Whether we have already build the CI image in this run


def ci(cxt, command, flags='', pty=False):
    """Run a task inside the CI container.

    Parameters:
        cxt (invoke.Context): The context to run the command in.
        command (str): The command to run inside the container.
        flags (str): Any extra Docker flags to add to the command.
        pty (bool): Whether to use a PTY for the command.
    """
    if not IN_CI_ENVIRONMENT:
        command_template = (
            'docker run'
            ' --rm'
            ' --env CI=true'
            ' --workdir "{workdir}"'
            ' --volume "{pwd}:{workdir}"'
            ' {flags}'
            ' {ci_image}'
            ' {command}')

        command = command_template.format(
            workdir='/package',
            pwd=os.getcwd(),
            flags=flags,
            ci_image=CI_IMAGE,
            command=command)

    cxt.run(command, pty=pty, shell='/bin/sh')


@task
def build_ci(cxt):
    """Build the CI image."""
    global BUILT_CI # Allow assignment in the global scope

    if not IN_CI_ENVIRONMENT and not BUILT_CI:
        command = 'docker build --tag {ci_image} .'
        cxt.run(command.format(ci_image=CI_IMAGE))

        BUILT_CI = True

@task
def run_ci(cxt):
    """Run the CI environment and launch a shell."""
    build_ci(cxt)

    ci(cxt, 'sh', flags='-it', pty=True)

@task
def build_docs(cxt):
    """Build the documentation."""
    build_ci(cxt)

    command = 'make -C {docs_dir} html'
    ci(cxt, command.format(docs_dir=DOCS_DIR))

@task
def serve_docs(cxt, port=8080):
    """Serve the documentation by default on port 8080."""
    build_docs(cxt)

    command = 'cd "{html_dir}" && python3 -m http.server {port}'
    command = command.format(
        html_dir='{docs_dir}/_build/html'.format(docs_dir=DOCS_DIR),
        port=port)

    cxt.run(command, pty=True)

@task
def test(cxt):
    """Run all tests."""
    unit_test(cxt)
    test_install(cxt)

@task
def unit_test(cxt):
    """Run the unit tests."""
    build_ci(cxt)

    command = 'coverage run -m unittest {tests_file}'
    ci(cxt, command.format(tests_file=TESTS_FILE))

@task
def test_install(cxt):
    """Test that the package installs with PIP."""
    ci(cxt, 'pip install .')

@task
def lint(cxt):
    """Run the linters."""
    lint_module(cxt)
    lint_tests(cxt)

@task
def lint_module(cxt):
    """Run the linters on the module."""
    build_ci(cxt)

    command = 'pylint --reports no {module} setup.py'
    ci(cxt, command.format(module=MODULE_NAME))

    command = 'flake8 {module} setup.py'
    ci(cxt, command.format(module=MODULE_NAME))

@task
def lint_tests(cxt):
    """Run the linters on the tests."""
    build_ci(cxt)

    command = (
        'pylint'
        ' --reports no'
        ' --disable protected-access'
        ' --disable missing-docstring'
        ' {tests_file}')
    ci(cxt, command.format(tests_file=TESTS_FILE))

    command = 'flake8 --ignore D100,D101,D102,D103,D107 {tests_file}'
    ci(cxt, command.format(tests_file=TESTS_FILE))
