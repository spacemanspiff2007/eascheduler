# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys


IS_RTD_BUILD = os.environ.get('READTHEDOCS', '-').lower() == 'true'

# required for autodoc
sys.path.insert(0, os.path.join(os.path.abspath('..'), 'src'))


# -- Project information -----------------------------------------------------

project = 'EAScheduler'
copyright = '2024, spaceman_spiff'
author = 'spaceman_spiff'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx_autodoc_typehints',
    'sphinx_copybutton',
    'sphinx_exec_code',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-the-python-domain
add_module_names = False
# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-python_use_unqualified_type_names
python_use_unqualified_type_names = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'canonical_url': '',
    'logo_only': False,
    'version_selector': True,
    'language_selector': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#00b5bf',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}


# -- Options for intersphinx -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
if IS_RTD_BUILD:
    intersphinx_mapping = {
        'python': ('https://docs.python.org/3', None),
        'whenever': ('https://whenever.readthedocs.io/en/stable', None)
    }
