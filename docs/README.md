# Documentation

Documentation is built using Sphinx.

## Dependencies

[Sphinx](https://pypi.python.org/pypi/Sphinx), [sphinx_autodoc_typehints](https://pypi.python.org/pypi/sphinx-autodoc-typehints), [sphinx_rtd_theme](https://pypi.python.org/pypi/sphinx_rtd_theme) must be installed to build html documentation, which is done using the `make html` command.

To rebuild API documentation after the API has changed, Python 3.6 must be used, and [better-apidoc](https://pypi.python.org/pypi/better-apidoc/) must be installed. API documentation is rebuilt using the `make api` command.
