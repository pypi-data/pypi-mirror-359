graphdict
=========

.. image:: https://img.shields.io/pypi/v/graphdict.svg
   :target: https://pypi.org/project/graphdict/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/l/graphdict.svg
   :target: https://github.com/taylortech75/graphdict/blob/main/LICENSE.txt
   :alt: License

.. image:: https://img.shields.io/pypi/pyversions/graphdict.svg
   :target: https://pypi.org/project/graphdict/
   :alt: Supported Python Versions

.. image:: https://img.shields.io/github/labels/taylortech75/graphdict/good%20first%20issue?color=green&label=contribute
   :target: https://github.com/taylortech75/graphdict/contribute
   :alt: Good First Issue

**graphdict** is a Python package for the creation, manipulation, and analysis of graph data structures and algorithms.  
It offers a lightweight, dictionary-based API to build and explore complex networks.

Resources
---------

- **Source code:** https://github.com/taylortech75/graphdict
- **Issue tracker:** https://github.com/taylortech75/graphdict/issues
- **Discussions:** https://github.com/taylortech75/graphdict/discussions
- **Security reporting:** https://tidelift.com/security
- **Documentation (coming soon):** https://taylortech75.github.io/graphdict

Simple Example
--------------

Find the shortest path between two nodes in an undirected graph:

.. code:: pycon

    >>> import graphdict as nx
    >>> G = nx.Graph()
    >>> G.add_edge("A", "B", weight=4)
    >>> G.add_edge("B", "D", weight=2)
    >>> G.add_edge("A", "C", weight=3)
    >>> G.add_edge("C", "D", weight=4)
    >>> nx.shortest_path(G, "A", "D", weight="weight")
    ['A', 'B', 'D']

Install
-------

Install the latest released version:

.. code:: shell

    pip install graphdict

Install with optional dependencies:

.. code:: shell

    pip install graphdict[default]

For more information, refer to the `installation guide <https://networkx.org/documentation/stable/install.html>`_.

Bugs & Contributions
--------------------

Please report bugs or issues on the `issue tracker <https://github.com/taylortech75/graphdict/issues>`_.

We welcome contributions of all kinds!  
You can fork the repo, make your changes, and open a pull request.  
If you're new to open source or Git, feel free to ask questions on the issue — we're happy to help.

See our `contributor guide <https://networkx.org/documentation/latest/developer/contribute.html>`_ for tips.

License
-------

Released under the `3-Clause BSD License <https://github.com/taylortech75/graphdict/blob/main/LICENSE.txt>`_::

    Copyright (c) 2004–2025, graphdict Developers
    John Smith <johnsmithdev92@gmail.com>
