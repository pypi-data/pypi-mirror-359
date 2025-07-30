from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prepo",
    version="0.1.1",
    author="Erik Hoxhaj",
    author_email="erik.hoxhaj@outlook.com",
    description="A package for preprocessing pandas DataFrames",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/erikhox/prepo",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "scikit-learn>=0.22.0",
        "scipy>=1.4.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "flake8>=3.8.0",
            "black>=20.8b1",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/erikhox/prepo/issues",
        "Source": "https://github.com/erikhox/prepo",
        "Documentation": "https://github.com/erikhox/prepo#readme",
    },
    keywords="pandas preprocessing data-science feature-engineering",

)
