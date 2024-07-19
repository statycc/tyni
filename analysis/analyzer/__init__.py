from typing import Optional, Type

# flake8: noqa: F401
from .base import AbstractAnalyzer, BaseVisitor
from .java import JavaAnalyzer
from .json import JsonLoader


def choose_analyzer(input_file: str) -> Optional[Type[AbstractAnalyzer]]:
    if JavaAnalyzer.lang_match(input_file):
        return JavaAnalyzer
    if JsonLoader.lang_match(input_file):
        return JsonLoader
    return None
