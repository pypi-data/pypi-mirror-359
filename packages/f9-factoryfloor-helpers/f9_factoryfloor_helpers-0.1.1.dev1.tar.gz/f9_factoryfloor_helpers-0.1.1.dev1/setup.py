from setuptools import setup, find_packages

setup(
    name="f9-factoryfloor-helpers",
    version="0.1.1-dev1",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "nagerapi",
        "five9-python>=0.0.4.dev3",
        "datetime",
    ],
    author="FactoryFloor Team",
    author_email="team@factoryfloor.example.com",
    description="Helper tools for FactoryFloor projects",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/factoryfloor/factoryfloor-helpers",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)