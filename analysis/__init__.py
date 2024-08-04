__title__ = "analysis"
__author__ = "Clément Aubert and Neea Rusch"
__license__ = ""
__version__ = "0.1.0"

# flake8: noqa: F401
from . import utils
from .utils import Bcolors as Colors
from .result import DirResult, Result, Timeable
from .result import AnalysisResult, ClassResult, MethodResult
from .evaluate import Evaluate
