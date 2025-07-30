from setuptools import setup, find_packages

# Read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="Fourier_Classification",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.0.0",
        "plotly>=4.14.0",
        "tensorflow>=2.4.0",
        "matplotlib>=3.3.0",
        "scikit-learn>=0.24.0",
    ],
    author="Abbass Srour",
    author_email="abbasss@umich.edu",
    description="A package for classifying 1D signals using Fourier Series and Machine Learning",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://github.com/abbass12/FourierSeriesClassification",
    keywords="fourier, signal processing, machine learning, classification",
    python_requires=">=3.6",
)
