from setuptools import setup, find_packages

setup(
    name="Calculator2",
    version="0.1.0",
    packages=find_packages(),
    description="Even if it is nothing but for easier codes without adding anything I created this library to calculate",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Dennis",
    url="https://github.com/2232MATTIA/Calculator",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
