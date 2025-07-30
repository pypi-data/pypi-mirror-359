"""
This module contains functionality to dynamically load data when
executing a pipeline or workflow. It can be imported as follows:

>>> from dtaianomaly import data

Custom data loaders can be implemented by extending :py:class:`~dtaianomaly.data.LazyDataLoader`.
"""

from .DataSet import DataSet
from .LazyDataLoader import LazyDataLoader
from .PathDataLoader import PathDataLoader, from_directory
from .simple_time_series import (
    DemonstrationTimeSeriesLoader,
    demonstration_time_series,
    make_sine_wave,
)
from .UCRLoader import UCRLoader

__all__ = [
    "LazyDataLoader",
    "PathDataLoader",
    "DataSet",
    "from_directory",
    "demonstration_time_series",
    "DemonstrationTimeSeriesLoader",
    "make_sine_wave",
    "UCRLoader",
]
