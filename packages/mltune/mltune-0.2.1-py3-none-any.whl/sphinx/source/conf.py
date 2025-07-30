# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'mltune'
copyright = '2025, Volodymyr Gnateiko'
author = 'Volodymyr Gnateiko'
release = '0.2.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx.ext.viewcode',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = []

napoleon_google_docstring = False
napoleon_numpy_docstring = True

import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

autodoc_member_order = 'bysource'
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_baseurl = 'https://birrgrrim.github.io/mltune/'
html_theme_options = {
    'canonical_url': 'https://birrgrrim.github.io/mltune/',
    'style_external_links': True
}
html_extra_path = []
html_static_path = ['_static']
html_logo = None
html_static_path = ['_static']
html_css_files = []
html_js_files = []
html_theme = 'sphinx_rtd_theme'
html_context = {
    'display_github': True,
    'github_user': 'birrgrrim',
    'github_repo': 'mltune',
    'github_version': 'main',
    'conf_py_path': '/docs/',
}
