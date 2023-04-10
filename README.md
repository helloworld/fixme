# fixme

[![PyPI](https://img.shields.io/pypi/v/fixme.svg)](https://pypi.org/project/fixme/)
[![Changelog](https://img.shields.io/github/v/release/helloworld/fixme?include_prereleases&label=changelog)](https://github.com/helloworld/fixme/releases)
[![Tests](https://github.com/helloworld/fixme/actions/workflows/test.yml/badge.svg)](https://github.com/helloworld/fixme/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/helloworld/fixme/blob/master/LICENSE)

Use AI to automatically fix bugs

## Installation

Install this tool using `pip`:

    pip install fixme

## Usage

For help, run:

    fixme --help

You can also use:

    python -m fixme --help

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd fixme
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest
