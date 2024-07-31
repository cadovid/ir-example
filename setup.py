from setuptools import setup, find_packages


setup(
    name="example-ir",
    version="v1.0.0",
    author="cadovid",
    author_email="david.camino.perdones@gmail.com",
    description="An example of Information Retrieval system deployed as a REST API endpoint",
    url="https://github.com/cadovid/ir-example",
    python_requires=">=3.9",
    packages=find_packages()
)
