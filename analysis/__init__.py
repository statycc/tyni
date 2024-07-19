__title__ = "analysis"
__author__ = "Clément Aubert and Neea Rusch"
__license__ = ""
__version__ = "0.0.1"

# flake8: noqa: F401
from . import utils
from .utils import Bcolors as Colors
from .result import Result, Timeable
from .result import AnalysisResult, ClassResult, MethodResult
from .evaluate import Evaluate
