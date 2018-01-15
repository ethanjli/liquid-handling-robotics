# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXAPIDOC  = better-apidoc
SPHINXPROJ    = lhrhost
SOURCEDIR     = source
APIDIR        = "$(SOURCEDIR)/api"
APITEMPLATES  = "$(SOURCEDIR)/_templates"
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Generate API stubs
api: export PYTHONPATH := ../
api:
	@$(SPHINXAPIDOC) -fMeT -t "$(APITEMPLATES)" -o "$(APIDIR)" "../"
	@echo "Auto-generation of API documentation finished." \
		"The generated api files are in $(APIDIR)."

# Remove auto-generated files
clean:
	@rm -rf "$(BUILDDIR)"
	@rm -rf "$(APIDIR)"

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
