# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'PyDriftn'
copyright = '2024, Australian Astronomical Optics' 
author = 'Australian Astronomical Optics'

# The short X.Y version.
version = "1.0"

# The full version, including alpha/beta/rc tags (using semantic versioning,
# cf. https://semver.org)
release = '0.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",
    'sphinx.ext.graphviz',
    'sphinx.ext.inheritance_diagram'
]

inheritance_graph_attrs = dict(rankdir="TB", size='""')

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', "desktop.ini", "*.xcf"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = f"{project} v{release}"
html_favicon = "_static/aao-favicon.png"
  

html_copy_source = False
html_show_sourcelink = False
html_domain_indices = False

if True:
    html_theme = "nature"
    html_theme_options = {
        "globaltoc_includehidden": True,
        "sidebarwidth": 256,
        "navigation_with_keys": False,
    }
    html_sidebars = {
        "**": [
            "searchbox.html",
            "localtoc.html",
            "globaltoc.html",
            "relations.html",
            "sourcelink.html",
        ],
        "index": ["searchbox.html", "localtoc.html", "globaltoc.html"],
    }
    html_css_files = ["pare-nature.css"]
else:
    html_theme = "pydata_sphinx_theme"
    html_theme_options = {
        "show_nav_level": 0,
        "navigation_with_keys": False,
    }

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#
html_logo = "_static/AAO_logo_black.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

autodoc_default_options = {"member-order": "groupwise"}

latex_engine = "xelatex"
