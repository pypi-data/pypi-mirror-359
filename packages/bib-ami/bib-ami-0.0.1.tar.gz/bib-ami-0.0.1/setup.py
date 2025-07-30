from setuptools import setup, find_packages

setup(
    name="bib-ami",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "bib-ami = bib_ami.bib_ami:main",
        ],
    },
    author="Rolf Carlson",
    author_email="hrolfrc@gmail.com",
    description="A tool to merge and clean BibTeX files.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/hrolfrc/bib-ami",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
