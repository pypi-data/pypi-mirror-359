"""
PyInGraph 🐷 - A Python-based framework for graphically integrating multiple Python algorithms
"""

__version__ = "0.1.7"
__author__ = "bobobone"
__email__ = "bobobone@qq.com"

from .PyG_graph_load import GraphLoader
from .PyG_node_interface import BlockBase
from .examples_utils import (
    get_examples_path,
    list_examples,
    copy_examples,
    copy_example,
    show_example_usage
)

__all__ = [
    'GraphLoader',
    'BlockBase',
    'get_examples_path',
    'list_examples', 
    'copy_examples',
    'copy_example',
    'show_example_usage'
]