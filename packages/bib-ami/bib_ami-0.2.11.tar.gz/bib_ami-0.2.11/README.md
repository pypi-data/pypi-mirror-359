# bib-ami

[![CircleCI](https://circleci.com/gh/hrolfrc/bib-ami.svg?style=shield)](https://circleci.com/gh/hrolfrc/bib-ami)
[![ReadTheDocs](https://readthedocs.org/projects/bib-ami/badge/?version=latest)](https://bib-ami.readthedocs.io/en/latest/)
[![Codecov](https://codecov.io/gh/hrolfrc/bib-ami/branch/master/graph/badge.svg)](https://codecov.io/gh/hrolfrc/bib-ami)

A Python tool to merge, deduplicate, and clean BibTeX files. It consolidates `.bib` files from a directory, removes duplicate entries, validates DOIs, scrapes missing DOIs using CrossRef/DataCite APIs, and refreshes metadata for accurate citations, especially for AI-generated references.

## Installation

```bash
pip install bib-ami