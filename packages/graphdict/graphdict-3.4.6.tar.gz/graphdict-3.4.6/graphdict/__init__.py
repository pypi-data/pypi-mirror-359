"""
graphdict
========

graphdict is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

See https://graphdict.org for complete documentation.
"""

__version__ = "3.4.6"


# These are imported in order as listed
from graphdict.lazy_imports import _lazy_import

from graphdict.exception import *

from graphdict import utils
from graphdict.utils import _clear_cache, _dispatchable

# load_and_call entry_points, set configs
config = utils.backends._set_configs_from_environment()
utils.config = utils.configs.config = config  # type: ignore[attr-defined]

from graphdict import classes
from graphdict.classes import filters
from graphdict.classes import *

from graphdict import convert
from graphdict.convert import *

from graphdict import convert_matrix
from graphdict.convert_matrix import *

from graphdict import relabel
from graphdict.relabel import *

from graphdict import generators
from graphdict.generators import *

from graphdict import readwrite
from graphdict.readwrite import *

# Need to test with SciPy, when available
from graphdict import algorithms
from graphdict.algorithms import *

from graphdict import linalg
from graphdict.linalg import *

from graphdict import drawing
from graphdict.drawing import *


def __getattr__(name):
    if name == "random_tree":
        raise AttributeError(
            "nx.random_tree was removed in version 3.4. Use `nx.random_labeled_tree` instead.\n"
            "See: https://graphdict.org/documentation/latest/release/release_3.4.html"
        )
    raise AttributeError(f"module 'graphdict' has no attribute '{name}'")
