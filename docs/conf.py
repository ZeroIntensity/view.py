# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "view.py"
copyright = "2026, Peter Bierma"
author = "Peter Bierma"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.intersphinx",
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
]
autosummary_generate = True
add_module_names = False  # Cleaner output

# This is the key part for making detailed pages:
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "shibuya"
html_theme_options = {
    "accent_color": "blue",
    "light_logo": "_static/logo_black.svg",
    "dark_logo": "_static/logo_white.svg",
    "logo_target": "https://view.zintensity.dev",
    "github_url": "https://github.com/ZeroIntensity/view.py",
    "announcement": "view.py is currently in alpha and not considered ready for production",
}
html_static_path = ["_static"]
html_favicon = "_static/favicon.ico"
html_context = {
    "source_type": "github",
    "source_user": "ZeroIntensity",
    "source_repo": "view.py",
    "source_version": "main",
    "source_docs_path": "/docs/",
}
