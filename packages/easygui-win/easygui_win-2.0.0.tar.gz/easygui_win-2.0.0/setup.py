#!/usr/bin/env python3
"""
Setup script for EasyGUI - A super simple Windows GUI library
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "EasyGUI - A super simple Windows GUI library for Python"

# Read version from the package
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), 'easygui', '__init__.py')
    if os.path.exists(version_file):
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip('"').strip("'")
    return "2.0.0"

setup(
    name="easygui-win",
    version=get_version(),
    author="Mr. Alien",
    author_email="shutussx@gmail.com",
    description="A super simple Windows GUI library for Python",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/shutussx/easygui-win",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: User Interfaces",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - pure Python with Windows API
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
            "mypy",
        ],
    },
    entry_points={
        "console_scripts": [
            "easygui-demo=easygui.demos:main",
        ],
    },
    keywords="gui windows ui desktop simple easy",
    project_urls={
        "Bug Reports": "https://github.com/shutussx/easygui-win/issues",
        "Source": "https://github.com/shutussx/easygui-win",
        "Documentation": "https://github.com/shutussx/easygui-win/blob/main/README.md",
    },
    include_package_data=True,
    zip_safe=False,
)