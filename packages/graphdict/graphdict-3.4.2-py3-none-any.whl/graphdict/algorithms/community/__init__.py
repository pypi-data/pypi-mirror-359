"""Functions for computing and measuring community structure.

The ``community`` subpackage can be accessed by using :mod:`networkx.community`, then accessing the
functions as attributes of ``community``. For example::

    >>> import graphdict as nx
    >>> G = nx.barbell_graph(5, 1)
    >>> communities_generator = nx.community.girvan_newman(G)
    >>> top_level_communities = next(communities_generator)
    >>> next_level_communities = next(communities_generator)
    >>> sorted(map(sorted, next_level_communities))
    [[0, 1, 2, 3, 4], [5], [6, 7, 8, 9, 10]]

"""

from graphdict.algorithms.community.asyn_fluid import *
from graphdict.algorithms.community.centrality import *
from graphdict.algorithms.community.divisive import *
from graphdict.algorithms.community.kclique import *
from graphdict.algorithms.community.kernighan_lin import *
from graphdict.algorithms.community.label_propagation import *
from graphdict.algorithms.community.lukes import *
from graphdict.algorithms.community.modularity_max import *
from graphdict.algorithms.community.quality import *
from graphdict.algorithms.community.community_utils import *
from graphdict.algorithms.community.louvain import *
from graphdict.algorithms.community.leiden import *
from graphdict.algorithms.community.local import *
