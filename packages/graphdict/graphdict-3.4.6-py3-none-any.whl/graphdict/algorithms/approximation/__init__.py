"""Approximations of graph properties and Heuristic methods for optimization.

The functions in this class are not imported into the top-level ``networkx``
namespace so the easiest way to use them is with::

    >>> from graphdict.algorithms import approximation

Another option is to import the specific function with
``from graphdict.algorithms.approximation import function_name``.

"""

from graphdict.algorithms.approximation.clustering_coefficient import *
from graphdict.algorithms.approximation.clique import *
from graphdict.algorithms.approximation.connectivity import *
from graphdict.algorithms.approximation.distance_measures import *
from graphdict.algorithms.approximation.dominating_set import *
from graphdict.algorithms.approximation.kcomponents import *
from graphdict.algorithms.approximation.matching import *
from graphdict.algorithms.approximation.ramsey import *
from graphdict.algorithms.approximation.steinertree import *
from graphdict.algorithms.approximation.traveling_salesman import *
from graphdict.algorithms.approximation.treewidth import *
from graphdict.algorithms.approximation.vertex_cover import *
from graphdict.algorithms.approximation.maxcut import *
from graphdict.algorithms.approximation.density import *
