"""
Pyroform Setup Configuration
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

#   with open("requirements.txt", "r", encoding="utf-8") as fh:
#       requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="pyroform",
    version="0.1.0",
    author="Pyroform Team",
    description="Linux Configurator tool written in Python3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
#   install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pyroform=pyroform.cli:main",
        ],
    },
)

# CODE DUMP

#   # setup.py
#   from setuptools import setup, find_packages

#   setup(
#       name="pyroform",
#       version="0.1.0",
#       packages=find_packages(),
#       install_requires=[
#           "flow-ctrl>=1.0.0",
#           "PyYAML>=6.0",
#           "click>=8.0.0"
#       ],
#       entry_points={
#           'console_scripts': [
#               'pyroform=pyroform.cli:main',
#           ],
#       }
#   )
