from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="InformationGain",
    version="0.1.2",
    description="A Python package for calculating information gain.",
    long_description=long_description,
    long_description_content_type="text/markdown",  # This tells PyPI it's markdown
    author="Abhinav Masih",
    author_email="abhnv.msh@gmail.com",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.12",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
