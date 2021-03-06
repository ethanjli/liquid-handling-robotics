# Documentation

Documentation is built using Sphinx.

## Dependencies

[Sphinx](https://pypi.python.org/pypi/Sphinx), [sphinx_autodoc_typehints](https://pypi.python.org/pypi/sphinx-autodoc-typehints), [Graphviz](https://www.graphviz.org/), [PlantUML](http://plantuml.com/), [sphinxcontrib-plantuml](https://pypi.org/project/sphinxcontrib-plantuml/), and [sphinx_rtd_theme](https://pypi.python.org/pypi/sphinx_rtd_theme) must be installed to build html documentation, which is done using the `make html` command.

To rebuild API documentation after the API has changed, Python 3.6 must be used, and [better-apidoc](https://pypi.python.org/pypi/better-apidoc/) must be installed. API documentation is rebuilt using the `make api` command.

To serve the documentation on a local web server and automatically update it in response to changes in the documentation, [sphinx-autobuild](https://pypi.org/project/sphinx-autobuild/) must be installed. The local web serve is started using the `make livehtml` command.

