#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_namespace_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["dbt-core~=1.0.1", "cx_Oracle==8.1.0"]

setup_requirements = []

test_requirements = ["pytest-dbt-adapter==0.4.0"]

setup(
    author="Indicium Tech",
    author_email="vitor.avancini@indicium.tech",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="An Oracle DBT Adapater",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="dbt-oracle",
    name="dbt-oracle",
    packages=find_namespace_packages(include=["dbt", "dbt.*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/eredzik/dbt-oracle",
    version="0.5.0",
)
