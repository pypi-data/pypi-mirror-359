from setuptools import setup, find_packages


setup(
    name="kid_sdk",
    version="1.2",
    author="Zonesmart",
    author_email="e.beliakov@dev.kokoc.com",
    packages=find_packages(),
    install_requires=[
        "authlib",
        "requests",
        "pendulum",
    ],
)
