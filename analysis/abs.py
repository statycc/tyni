from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AbstractAnalyzer(ABC):
    def __init__(self, input_file: str, out_file: str = None):
        """Base class for an analyzer.

        Arguments:
            input_file: input program to analyze.
            out_file: FILE for analysis results [default: None].
        """
        self.input_file = input_file
        self.out_file = out_file
        self.tree = None

    @staticmethod
    def lang_match(input_file: str) -> bool:
        """Determines if analyzer can handle input file.

        Arguments:
            input_file: input program to analyze.

        Returns:
            True is file seems analyzable.
        """
        return False

    @abstractmethod
    def parse(self) -> AbstractAnalyzer:
        """Parses the input file.

        Returns:
            The analyzer object.
        """
        pass

    @abstractmethod
    def run(self) -> dict:
        """Analyzes input file.

        Returns:
            The analysis results as a dictionary.
        """
        pass

    def save(self, data: dict) -> None:
        """Saves analysis results to file.

        Arguments:
            data: analysis results.
        """
        assert self.out_file
        content = {'input_prog': self.input_file, 'result': data}
        dir_path, _ = os.path.split(self.out_file)
        if len(dir_path) > 0 and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(self.out_file, "w") as outfile:
            json.dump(content, outfile, indent=4)
        logger.info(f'Wrote result to: {self.file_name}')

    @staticmethod
    def default_out(input_file, out_dir='out', path_depth=3) -> str:
        """Helper to generate output file name for input file.

        Arguments:
            input_file: program file path.
            out_dir: path to output directory [default:output].
            path_depth: number of directories to include [default:3].

        Returns:
            The generated file name.
        """
        dir_depth = -(path_depth + 1)  # +1 for the filename
        file_only = os.path.splitext(input_file)[0]
        file_name = '_'.join(file_only.split('/')[dir_depth:])
        return os.path.join(out_dir, f"{file_name}.json")

    @staticmethod
    def pretty_print(result):
        for cls in result.values():
            print(cls)


class BaseVisitor:
    @staticmethod
    def wclr(s: str, desc: str = ""):
        desc_ = f" {desc}" if desc else ""
        colored = f'{bcolors.WARNING}{s}{bcolors.ENDC}'
        logger.warning(f'unhandled{desc_} {colored}')


class ResultObj(dict):
    @staticmethod
    def coloring(s: str):
        return f'{bcolors.OKBLUE}{s}{bcolors.ENDC}'


class ClassResult(ResultObj):
    def __init__(self, name: str, methods: dict[MethodResult]):
        super().__init__()
        self.name = name
        self.methods = list(methods.keys())
        for (k, v) in methods.items():
            super().__setitem__(k, v)

    def __str__(self):
        sep = "\n" + ('-' * 52) + '\n'
        c_name = self.coloring(self.name)
        methods = sep.join(
            [str(self.__getitem__(m)) for m in self.methods])
        return f'class {c_name}{sep}{methods}'


class MethodResult(ResultObj):
    def __init__(self, name: str, source: str, flows: list[list[str]],
                 variables: dict[str, str]):
        super().__init__()
        self.name = name
        super().__setitem__('variables', list(variables))
        super().__setitem__('source', source)
        super().__setitem__('flows', flows)

    @staticmethod
    def flow_fmt(tpl):
        return MethodResult.coloring(f'{tpl[0]}🌢{tpl[1]}')

    def joiner(self, key, fmt=None):
        f = fmt or self.coloring
        return (", ".join(map(f, self.__getitem__(key)))
                or self.coloring('-'))

    def __str__(self):
        code = self.__getitem__("source")
        vars_ = self.joiner("variables")
        flows = self.joiner("flows", self.flow_fmt)
        m_name = self.coloring(self.name)
        return (f'Method: {m_name}\n{code}\n'
                f'Vars:   {vars_}\nFlows:  {flows}')


# noinspection PyClassHasNoInit,PyPep8Naming
class bcolors:
    """From https://stackoverflow.com/a/287944"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
