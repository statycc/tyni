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
        content = {'input': self.input_file, 'result': data}
        dir_path, _ = os.path.split(self.out_file)
        if len(dir_path) > 0 and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(self.out_file, "w") as outfile:
            json.dump(content, outfile, indent=4)
        logger.info(f'Wrote result to: {self.out_file}')

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


class BaseVisitor(ABC):
    """Base class for a parse-tree visitor."""

    @staticmethod
    def skipped(ctx, desc: str = "") -> None:
        """Displays a colored warning.

        Arguments:
            ctx: parse tree context.
            desc: optional description.
        """
        text = BaseVisitor.og_text(ctx)
        desc_ = f" {desc}" if desc else ""
        colored = f'{bcolors.WARNING}{text}{bcolors.ENDC}'
        logger.warning(f'unhandled{desc_} {colored}')

    @staticmethod
    def og_text(ctx) -> str:
        """Get the original of a parse tree node.

        Arguments:
            ctx: tree node

        Returns:
            Node text with original whitespaces.
        """
        token_source = ctx.start.getTokenSource()
        input_stream = token_source.inputStream
        start, stop = ctx.start.start, ctx.stop.stop
        return input_stream.getText(start, stop)

    @staticmethod
    def uniq_name(init, known):
        """Find a unique replacement name for a variable.

        By "reverse pigeon-hole", this method always finds
        a unique name. The name is illegal in the input
        language, so that it is known, such name always
        came from renaming.

        Arguments:
            init: initial name.
            known: list of known names.

        Returns:
            A new name that is not in the known names.
        """
        for i in range(2, len(known) + 2 + 1):
            candidate = f'{init}{BaseVisitor.u_sub(i)}'
            if candidate not in known:
                return candidate

    @staticmethod
    def u_sub(n: int):
        """Unicode subscript of a positive int."""
        assert n >= 0
        numbers = '₀,₁,₂,₃,₄,₅,₆,₇,₈,₉'.split(',')
        int_chars = [int(c) for c in str(n)]
        return ''.join([numbers[i] for i in int_chars])


class ResultObj(dict):
    """Base class for a capturing analysis results."""

    LN_LEN = 52

    @staticmethod
    def coloring(text: str) -> str:
        """Adds color to text.

        Arguments:
            text: text to color.

        Returns:
            The original text with added color.
        """
        return f'{bcolors.OKBLUE}{text}{bcolors.ENDC}'


class ClassResult(ResultObj):
    def __init__(self, name: str, methods: dict[MethodResult]):
        super().__init__()
        self.update(methods)
        self.name = name

    def __str__(self):
        sep = "\n" + ('-' * self.LN_LEN) + '\n'
        c_name = self.coloring(self.name)
        items = map(str, self.values())
        return f'class {c_name}{sep}{sep.join(items)}'


class MethodResult(ResultObj):
    FLW_SEP = "🌢"

    def __init__(self, name: str, source: str, flows: list[list[str]],
                 variables: dict[str, str]):
        super().__init__()
        super().__setitem__('variables', list(variables))
        super().__setitem__('source', source)
        super().__setitem__('flows', flows)
        self.name = name

    @staticmethod
    def flow_fmt(tpl):
        return MethodResult.coloring(
            f'{tpl[0]}{MethodResult.FLW_SEP}{tpl[1]}')

    @staticmethod
    def len_est(value):
        """estimate required chars to print a value"""
        if isinstance(value, str):
            return len(value)
        return sum([len(x) for x in value]) + 1

    @staticmethod
    def chunk(vals, max_w, sp):
        """splits printable values into chunks."""
        result, fst, acc = [], [], 0
        while vals:
            v = vals.pop(0)
            vl = sp + MethodResult.len_est(v)
            if acc + vl >= max_w:
                result.append(fst)
                fst, acc = [], 0
            acc, fst = acc + vl, fst + [v]
        return result + [fst]

    def join_(self, key, fmt=None):
        # line length and left padding
        w, lpad = self.LN_LEN - 8, 8
        # item formatting function
        f = fmt or self.coloring
        # separators for items and lines
        sep1, sep2 = ', ', '\n' + (' ' * lpad)
        # construct the output
        sorted_ = sorted(self.__getitem__(key))
        # split into lines by length
        chunks = self.chunk(sorted_, w, len(sep1))
        # format and join items in each line
        lines = [sep1.join(map(f, ch)) for ch in chunks]
        return sep2.join(lines) or self.coloring('-')

    def __str__(self):
        code = self.__getitem__("source")
        vars_ = self.join_("variables")
        flows = self.join_("flows", self.flow_fmt)
        name = self.coloring(self.name)
        return (f'{code}\n'
                f'Method: {name}\n'
                f'Vars:   {vars_}\n'
                f'Flows:  {flows}')


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
