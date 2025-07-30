from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="credit-risk-creditum",
    version="1.1.0",
    author="Omoshola Owolabi",
    author_email="owolabi.omoshola@outlook.com",
    description="Advanced credit risk assessment and stress testing with real-time economic data integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/credit-risk-creditum/creditum",
    project_urls={
        "Homepage": "https://crcreditum.com",
        "Documentation": "https://crcreditum.com/documentation",
        "Repository": "https://github.com/credit-risk-creditum/creditum",
        "Bug Reports": "https://github.com/credit-risk-creditum/creditum/issues",
        "PyPI": "https://pypi.org/project/credit-risk-creditum/",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "requests>=2.25.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    keywords="credit risk assessment fintech machine learning stress testing economic data",
    entry_points={
        "console_scripts": [
            "credit-risk=credit_risk.cli:main",
        ],
    },
)