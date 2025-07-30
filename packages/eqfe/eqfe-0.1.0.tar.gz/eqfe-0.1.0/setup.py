#!/usr/bin/env python3
"""
Setup script for Environmental Quantum Field Effects package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
with open(requirements_path, "r", encoding="utf-8") as f:
    requirements = [
        line.strip() for line in f if line.strip() and not line.startswith("#")
    ]

setup(
    name="environmental-quantum-field-effects",
    version="1.0.0",
    author="EQFE Research Team",
    author_email="eqfe@research.org",
    description="Investigation of environmental scalar field effects on quantum correlations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pelicansperspective/Environmental-Quantum-Field-Effects",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "isort>=5.9.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=0.5.0",
            "nbsphinx>=0.8.0",
        ],
        "quantum": [
            "cirq>=0.12.0",
            "qiskit>=0.28.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "eqfe-demo=examples.basic_demo:main",
            "eqfe-analyze=examples.advanced_analysis:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yaml", "*.yml"],
    },
    project_urls={
        "Bug Reports": "https://github.com/pelicansperspective/Environmental-Quantum-Field-Effects/issues",
        "Source": "https://github.com/pelicansperspective/Environmental-Quantum-Field-Effects",
        "Documentation": "https://eqfe.readthedocs.io/",
    },
)
