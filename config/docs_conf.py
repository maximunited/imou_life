# Configuration file for the Sphinx documentation builder.
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------

project = "Imou Life"
copyright = "2025, Imou Life Contributors"
author = "Imou Life Contributors"

# The full version, including alpha/beta/rc tags
release = "1.1.0"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "myst_parser",  # For Markdown support
    "sphinx.ext.napoleon",  # For Google style docstrings
    "sphinx.ext.autodoc",  # For auto documentation
    "sphinx.ext.viewcode",  # For source code viewing
    "sphinx.ext.intersphinx",  # For cross-referencing documentation
    "sphinx.ext.coverage",  # For code coverage
    "sphinx.ext.doctest",  # For testing docstrings
    "sphinx.ext.todo",  # For todo items
]

# The suffix of source filenames.
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# -- Options for Read the Docs ----------------------------------------------

# Read the Docs theme
html_theme = "sphinx_rtd_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.
html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "includehidden": True,
    "titles_only": False,
}
