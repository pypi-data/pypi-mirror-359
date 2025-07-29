# setup.py

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent

long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="grapes-tokenizer",
    version="0.1.1",
    author="Akash Pittalwar",
    author_email="akashpittalwar107@gmail.com",
    description="A simple sum-based tokenizer for NLP/LLM research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/akashpittalwar/Grapes-tokenizer",
    license="Apache-2.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(exclude=["tests*", "examples*"]),
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "grapes-tokenizer=grapes_tokenizer.cli:main",
        ]
    },
)
