import os

from setuptools import find_packages, setup

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
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        fixme=fixme.cli:cli
    """,
    install_requires=["click", "openai", "rich", "pydantic"],
    extras_require={
        "black": ["black"],
        "pyright": ["pyright"],
        "ruff": ["ruff"],
        "test": [
            "pytest",
        ],
    },
    python_requires=">=3.7",
)
