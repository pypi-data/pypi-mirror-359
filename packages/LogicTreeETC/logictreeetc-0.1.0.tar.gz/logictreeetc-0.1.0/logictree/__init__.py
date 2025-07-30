"""
LogicTreeETC: Flexible logic trees and multi-segment arrows with vertex-level control.

Modules:
- LogicTree: Create and connect labeled decision boxes.
- ArrowETC: Multi-segment arrows with explicit vertices.
- LogicBoxETC: Render styled, rotatable text boxes.

See the documentation for details and examples.
"""

__version__ = "0.1.0"
__author__ = "E. Tyler Carr"
__email__ = "carret1268@gmail.com"
__license__ = "CC0 1.0 Universal"

from .LogicTreeETC import LogicTree
from .ArrowETC import ArrowETC
from .LogicBoxETC import LogicBox

__all__ = [
    "LogicTree",
    "ArrowETC",
    "LogicBox",
]

import logging
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
