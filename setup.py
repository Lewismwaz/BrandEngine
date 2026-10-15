"""
Setup script for Brand Engine - creates a distributable package
"""
from setuptools import setup, find_packages  # pyright: ignore[reportMissingModuleSource]
import os
import sys

# Read requirements
with open('requirements.txt', 'r') as f:
    requirements = f.read().splitlines()

# Read README
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="BrandEngine",
    version="1.0.0",
    author="Yavuto",
    description="AI-Powered Brand Name Generator with Domain Checking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yavotu/brandengine",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'brandengine=main:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
)