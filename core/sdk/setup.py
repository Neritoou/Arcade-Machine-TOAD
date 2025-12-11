from setuptools import setup, find_packages

setup(
    name="arcade-machine-sdk",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[],
)
