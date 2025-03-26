from setuptools import setup, find_packages

setup(
    name="api-test",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.1",
        "requests>=2.26.0",
    ],
    python_requires=">=3.6",
)
