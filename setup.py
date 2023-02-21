from setuptools import setup
import os

VERSION = "0.1"


def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()


setup(
    name="fixme",
    description="Use AI to automatically fix bugs",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="helloworld",
    url="https://github.com/helloworld/fixme",
    project_urls={
        "Issues": "https://github.com/helloworld/fixme/issues",
        "CI": "https://github.com/helloworld/fixme/actions",
        "Changelog": "https://github.com/helloworld/fixme/releases",
    },
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=["fixme"],
    entry_points="""
        [console_scripts]
        fixme=fixme.cli:cli
    """,
    install_requires=["click"],
    extras_require={
        "test": ["pytest"]
    },
    python_requires=">=3.7",
)
