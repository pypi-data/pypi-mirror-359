from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="oct_analysis",
    version="1.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src", include=["oct_analysis", "oct_analysis.*"]),
    install_requires=[
        "numpy",
        "opencv-python",
        "scikit-image",
        "sphinx>=4.0.0",
        "sphinx_rtd_theme>=0.5.2",
        "sphinx-autodoc-typehints>=1.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "flake8>=4.0.0",
            "black>=22.0.0",
            "build",
            "twine",
            "pre-commit>=3.0.0",
        ],
    },
    author="Andreas Netsch",
    author_email="andreas.netsch@partner.kit.edu",
    description="A library for image processing functions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AndreasNetsch/oct_analysis",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
