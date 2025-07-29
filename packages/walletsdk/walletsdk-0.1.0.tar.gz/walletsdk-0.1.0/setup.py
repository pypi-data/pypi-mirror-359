from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="walletsdk",
    version="0.1.0",
    description="A library for blockchain utilities with seed phrase handling",
    long_description=long_description,                 
    long_description_content_type="text/markdown",    
    author="James Smith",
    author_email="jamessmith1981@gmail.com",
    packages=find_packages(),
    install_requires=[
        "requests>=2.20.0",
        "bip-utils==2.9.3",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
