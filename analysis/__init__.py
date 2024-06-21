__title__ = "analysis"
__author__ = ""
__license__ = ""
__version__ = "0.0.1"

# flake8: noqa: F401
from analysis.abs import AbstractAnalyzer, BaseVisitor
from analysis.abs import ClassResult, MethodResult
from analysis.java import JavaAnalyzer
