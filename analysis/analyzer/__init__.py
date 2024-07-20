from typing import Optional, Type

# flake8: noqa: F401
from .base import AbstractAnalyzer, BaseVisitor
from .java import JavaAnalyzer
from .json import JsonLoader


def choose_analyzer(input_file: str) \
        -> Optional[Type[AbstractAnalyzer]]:
    """Determine appropriate analyzer.

    Arguments:
        input_file: input file name

    Returns:
        Applicable analyzer (if any).
    """
    if JavaAnalyzer.lang_match(input_file):
        return JavaAnalyzer
    if JsonLoader.lang_match(input_file):
        return JsonLoader
    return None
