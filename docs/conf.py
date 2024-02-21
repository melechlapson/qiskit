# This code is part of Qiskit.
#
# (C) Copyright IBM 2018.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

from __future__ import annotations

# pylint: disable=invalid-name,missing-function-docstring

"""Sphinx documentation builder."""

import datetime
import doctest
import inspect
import os
import re
import sys
from pathlib import PurePath

project = "Qiskit"
project_copyright = f"2017-{datetime.date.today().year}, Qiskit Development Team"
author = "Qiskit Development Team"

# The short X.Y version
version = "1.1"
# The full version, including alpha/beta/rc tags
release = "1.1.0"

language = "en"

rst_prolog = f".. |version| replace:: {version}"

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.doctest",
    # This is used by qiskit/documentation to generate links to github.com.
    "sphinx.ext.linkcode",
    "matplotlib.sphinxext.plot_directive",
    "reno.sphinxext",
    "sphinxcontrib.katex",
]

templates_path = ["_templates"]

# Number figures, tables and code-blocks if they have a caption.
numfig = True
# Available keys are 'figure', 'table', 'code-block' and 'section'.  '%s' is the number.
numfig_format = {"table": "Table %s"}

# Relative to source directory, affects general discovery, and html_static_path and html_extra_path.
exclude_patterns = ["_build", "**.ipynb_checkpoints"]


# This adds the module name to e.g. function API docs. We use the default of True because our
# module pages sometimes have functions from submodules on the page, and we want to make clear
# that you must include the submodule to import it. We should strongly consider reorganizing our
# code to avoid this, i.e. re-exporting the submodule members from the top-level module. Once fixed
# and verified by only having a single `.. currentmodule::` in the file, we can turn this back to
# False.
add_module_names = True

# A list of prefixes that are ignored for sorting the Python module index
# (e.g., if this is set to ['foo.'], then foo.bar is shown under B, not F).
modindex_common_prefix = ["qiskit."]

# ----------------------------------------------------------------------------------
# Intersphinx
# ----------------------------------------------------------------------------------

intersphinx_mapping = {
    "rustworkx": ("https://www.rustworkx.org/", None),
    "qiskit-ibm-runtime": ("https://docs.quantum.ibm.com/api/qiskit-ibm-runtime/", None),
    "qiskit-aer": ("https://qiskit.github.io/qiskit-aer/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
    "python": ("https://docs.python.org/3/", None),
}

# ----------------------------------------------------------------------------------
# HTML theme
# ----------------------------------------------------------------------------------

html_theme = "alabaster"
html_last_updated_fmt = "%Y/%m/%d"

# ----------------------------------------------------------------------------------
# Autodoc
# ----------------------------------------------------------------------------------

# Note that setting autodoc defaults here may not have as much of an effect as you may expect; any
# documentation created by autosummary uses a template file (in autosummary in the templates path),
# which likely overrides the autodoc defaults.

# Move type hints from signatures to the parameter descriptions (except in overload cases, where
# that's not possible).
autodoc_typehints = "description"
# Only add type hints from signature to description body if the parameter has documentation.  The
# return type is always added to the description (if in the signature).
autodoc_typehints_description_target = "documented_params"

autoclass_content = "both"

autosummary_generate = True
autosummary_generate_overwrite = False

# The pulse library contains some names that differ only in capitalisation, during the changeover
# surrounding SymbolPulse.  Since these resolve to autosummary filenames that also differ only in
# capitalisation, this causes problems when the documentation is built on an OS/filesystem that is
# enforcing case-insensitive semantics.  This setting defines some custom names to prevent the clash
# from happening.
autosummary_filename_map = {
    "qiskit.pulse.library.Constant": "qiskit.pulse.library.Constant_class.rst",
    "qiskit.pulse.library.Sawtooth": "qiskit.pulse.library.Sawtooth_class.rst",
    "qiskit.pulse.library.Triangle": "qiskit.pulse.library.Triangle_class.rst",
    "qiskit.pulse.library.Cos": "qiskit.pulse.library.Cos_class.rst",
    "qiskit.pulse.library.Sin": "qiskit.pulse.library.Sin_class.rst",
    "qiskit.pulse.library.Gaussian": "qiskit.pulse.library.Gaussian_class.rst",
    "qiskit.pulse.library.Drag": "qiskit.pulse.library.Drag_class.rst",
    "qiskit.pulse.library.Square": "qiskit.pulse.library.Square_fun.rst",
    "qiskit.pulse.library.Sech": "qiskit.pulse.library.Sech_fun.rst",
}

# We only use Google-style docstrings, and allowing Napoleon to parse Numpy-style docstrings both
# slows down the build (a little) and can sometimes result in _regular_ section headings in
# module-level documentation being converted into surprising things.
napoleon_google_docstring = True
napoleon_numpy_docstring = False


# ----------------------------------------------------------------------------------
# Doctest
# ----------------------------------------------------------------------------------

doctest_default_flags = (
    doctest.ELLIPSIS
    | doctest.NORMALIZE_WHITESPACE
    | doctest.IGNORE_EXCEPTION_DETAIL
    | doctest.DONT_ACCEPT_TRUE_FOR_1
)

# Leaving this string empty disables testing of doctest blocks from docstrings.
# Doctest blocks are structures like this one:
# >> code
# output
doctest_test_doctest_blocks = ""


# ----------------------------------------------------------------------------------
# Plot directive
# ----------------------------------------------------------------------------------

plot_html_show_formats = False


# ----------------------------------------------------------------------------------
# Source code links
# ----------------------------------------------------------------------------------

def determine_github_branch() -> str:
    """Determine the GitHub branch name to use for source code links.
    
    We need to decide whether to use `stable/<version>` vs. `main` for dev builds.
    Refer to https://docs.github.com/en/actions/learn-github-actions/variables
    for how we determine this with GitHub Actions.
    """
    # If not `GITHUB_REF_NAME` is not set, default to `main`. This
    # is relevant for local builds.
    if "GITHUB_REF_NAME" not in os.environ:
        return "main"

    # PR workflows set the branch they're merging into.
    if base_ref := os.environ.get("GITHUB_BASE_REF"):
        return base_ref

    ref_name = os.environ["GITHUB_REF_NAME"]
    if os.environ["GITHUB_REF_TYPE"] == "branch":
        return ref_name

    # Else, the ref_name is a tag like `1.0.0` or `1.0.0rc1`. We need
    # to transform this to a Git branch like `stable/1.0`.
    version_without_patch = re.match(r"(\d+\.\d+)", ref_name).group()
    return f"stable/{version_without_patch}"


GITHUB_BRANCH = determine_github_branch()


def linkcode_resolve(domain, info):
    if domain != "py":
        return None

    module = sys.modules.get(info["module"])
    if module is None:
        return None

    obj = module
    for part in info["fullname"].split("."):
        obj = getattr(obj, part)
        is_valid_code_object = (
            inspect.isclass(obj) or inspect.ismethod(obj) or inspect.isfunction(obj) and not inspect.isbuiltin(obj)
        )
        if not is_valid_code_object:
            return None

    full_file_name = inspect.getsourcefile(obj)
    if full_file_name is None or "qiskit" not in full_file_name:
        return None
    repo_root = PurePath(__file__).parent.parent
    file_name = PurePath(full_file_name).relative_to(repo_root)

    try:
        source, lineno = inspect.getsourcelines(obj)
    except OSError:
        linespec = ""
    else:
        ending_lineno = lineno + len(source) - 1
        linespec = f"#L{lineno}-L{ending_lineno}"

    return f"https://github.com/Qiskit/qiskit/tree/{GITHUB_BRANCH}/{file_name}{linespec}"
