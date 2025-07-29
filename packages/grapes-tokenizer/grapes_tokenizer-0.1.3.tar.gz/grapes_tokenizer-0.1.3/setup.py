# setup.py
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="grapes-tokenizer",
    version="0.1.3",
    author="Akash Pittalwar",
    author_email="akashpittalwar107@gmail.com",
    description="A simple sum-based tokenizer for NLP/LLM research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akashpittalwar/Grapes-tokenizer",
    project_urls={
        "Source": "https://github.com/akashpittalwar/Grapes-tokenizer",
        "Tracker": "https://github.com/akashpittalwar/Grapes-tokenizer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["tests*", "examples*"]),
    python_requires=">=3.6",
)
