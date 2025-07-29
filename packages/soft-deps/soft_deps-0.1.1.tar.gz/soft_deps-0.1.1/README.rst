
.. image:: https://readthedocs.org/projects/soft-deps/badge/?version=latest
    :target: https://soft-deps.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/soft_deps-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/soft_deps-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/soft_deps-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/soft_deps-project

.. image:: https://img.shields.io/pypi/v/soft-deps.svg
    :target: https://pypi.python.org/pypi/soft-deps

.. image:: https://img.shields.io/pypi/l/soft-deps.svg
    :target: https://pypi.python.org/pypi/soft-deps

.. image:: https://img.shields.io/pypi/pyversions/soft-deps.svg
    :target: https://pypi.python.org/pypi/soft-deps

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/soft_deps-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/soft_deps-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://soft-deps.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/soft_deps-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/soft_deps-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/soft_deps-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/soft-deps#files


Welcome to ``soft_deps`` Documentation
==============================================================================
.. image:: https://soft-deps.readthedocs.io/en/latest/_static/soft_deps-logo.png
    :target: https://soft-deps.readthedocs.io/en/latest/

soft-deps is a Python pattern for elegant optional dependency management that prioritizes developer experience over lazy loading. Unlike true lazy imports, soft-deps immediately attempts to import dependencies at module load time - if the dependency is installed, you get the real module with full functionality. If it's missing, you get a helpful proxy object that provides complete IDE type hints and auto-completion, but raises informative error messages only when you actually try to use the missing functionality.

This approach gives you the best of both worlds: seamless development experience with full IDE support when dependencies are available, and graceful degradation with clear installation guidance when they're not, all while maintaining zero code invasiveness in your implementation.


Quick Start
------------------------------------------------------------------------------
**Why use soft-deps?**

- **For library authors**: Provide optional features without forcing users to install heavy dependencies
- **For users**: Get full IDE support and autocomplete even for optional dependencies  
- **For teams**: Graceful degradation with clear error messages instead of cryptic import failures

**When to use soft-deps?**

Use soft-deps when your library has optional features that depend on external packages:

- Data science libraries with optional visualization (matplotlib, plotly)
- Web frameworks with optional database drivers (psycopg2, pymongo)  
- CLI tools with optional cloud integrations (boto3, google-cloud)
- Any library where you want some features to work without heavy dependencies

**How it works:**

Library authors use the soft-deps pattern in their code:

.. code-block:: python

    # your_library.py
    from soft_deps.api import MissingDependency

    # Try to import optional dependency
    try:
        import pandas as pd
    except ImportError:
        # Create helpful proxy if missing
        pd = MissingDependency("pandas", "pip install pandas")

    def export_to_excel(data):
        """Export data to Excel file (requires pandas)."""
        # IDE gets full autocomplete here even if pandas not installed
        # Error only occurs when this line actually executes
        return pd.DataFrame(data).to_excel("output.xlsx")

Users get seamless experience regardless of what's installed:

.. code-block:: python

    # user_script.py  
    from your_library import export_to_excel

    # This imports successfully even without pandas installed
    # IDE provides full autocomplete and type hints

    try:
        export_to_excel({"col1": [1, 2, 3]})
    except ImportError as e:
        print(e)  # "You didn't install pandas. To use DataFrame, pip install pandas"

**The difference:**

.. code-block:: python

    # ❌ Traditional approach - breaks immediately  
    import pandas as pd  # ImportError if not installed
    
    # ❌ Lazy imports - no IDE support
    def export_data():
        import pandas as pd  # IDE can't help with autocomplete
    
    # ✅ soft-deps - best of both worlds
    try:
        import pandas as pd
    except ImportError:
        pd = MissingDependency("pandas", "pip install pandas")
    # IDE gets full support, graceful errors when actually used


.. _install:

Install
------------------------------------------------------------------------------

``soft_deps`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install soft-deps

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade soft-deps
