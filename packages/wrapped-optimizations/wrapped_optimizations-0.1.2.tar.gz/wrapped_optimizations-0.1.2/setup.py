from setuptools import setup, find_packages

setup(
    name="wrapped_optimizations",
    version="0.1.2",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    description="A wrapper around some of scipy's optimization functions to allow for a more convenient use of parameters and constants.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Stephan Troyer",
    author_email="stephantroyer@live.at",
    url="https://github.com/stephtr/wrapped-optimizations",
    install_requires=[
        "numpy",
        "scipy",
    ],
)