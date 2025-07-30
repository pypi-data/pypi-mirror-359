# -*- coding: utf-8 -*-

import logging
import os
from sys import exit
from unittest import TestLoader, TextTestRunner

from click import echo, option
from click.decorators import group
from coverage import coverage, CoverageException


@group()
def cli_tests():
    pass


@cli_tests.command("run-tests")
@option("-t", "--test-type", "test_type", default="unit")
@option("-p", "--pattern", "pattern", default="tests*.py")
@option("-e", "--engine", "engine", default="unittest")
def run_tests(test_type: str, pattern: str, engine: str):
    """ Runs the tests """

    validate_engines(engine)
    if not os.path.exists(f"./tests/{test_type}"):
        echo(f"The directory: {test_type} does not exist under ./tests!", err=True)
        exit(1)

    if test_type == "unit":
        # Just removing verbosity from unit tests...
        os.environ["LOGGER_LEVEL"] = str(os.getenv("LOGGER_LEVEL_FOR_TEST", logging.ERROR))

    if engine == "pytest":
        pytest = import_pytest()
        test_path = f'./tests/{test_type}'
        args = [test_path, '-v', '-k', pattern.replace("s*.py", "")]

        exit_code = pytest.main(args)
        if exit_code != 0:
            exit(exit_code)

    else:
        tests = TestLoader().discover(f"./tests/{test_type}", pattern=pattern)
        result = TextTestRunner(verbosity=2).run(tests)
        if not result.wasSuccessful():
            exit(1)


@cli_tests.command("run-coverage")
@option("-s", "--save-report", "save_report", default=True)
@option("-e", "--engine", "engine", default="unittest")
def run_coverage(save_report: bool, engine: str):
    """ Runs the unit tests and generates a coverage report on success """

    validate_engines(engine)
    os.environ["LOGGER_LEVEL"] = str(os.getenv("LOGGER_LEVEL_FOR_TEST", logging.ERROR))
    coverage_ = coverage(branch=True, source=["."])
    coverage_.start()

    if engine == "unittest":
        tests = TestLoader().discover("./tests", pattern="tests*.py")
        result = TextTestRunner(verbosity=2).run(tests)

        if not result.wasSuccessful():
            exit(1)
    else:
        pytest = import_pytest()
        exit_code = pytest.main(["./tests", "-v"])

        if exit_code != 0:
            exit(exit_code)

    coverage_.stop()

    try:
        echo("Coverage Summary:")
        coverage_.report()

        if save_report:
            coverage_.save()
            coverage_.html_report()

        coverage_.erase()

    except CoverageException as error:
        echo(error)
        exit(1)


def validate_engines(engine: str) -> None:
    _engines = ["unittest", "pytest"]
    if engine not in _engines:
        echo(f"Valid engines: {_engines}", err=True)
        exit(1)


def import_pytest():
    # Because PyTest is an optional dependency, the import
    # statement is here...
    try:
        import pytest
        return pytest

    except ImportError:
        echo("PyTest is required. Execute: `pip install .[pytest]`", err=True)
        exit(1)
