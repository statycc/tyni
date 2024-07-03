from __future__ import annotations

import json
import logging
import os
import time

from . import Colors

logger = logging.getLogger(__name__)


class Result(dict):

    def __init__(self, in_: str, out_: str = None, save=False):
        super().__init__()
        self.infile = in_
        self.outfile = out_ or (self.default_out(in_) if save else None)

        # init timers
        self.timing = {'parse': {}, 'analysis': {}, 'eval': {}}
        self.t_parse = Timeable(self.timing, 'parse')
        self.t_analysis = Timeable(self.timing, 'analysis')
        self.t_eval = Timeable(self.timing, 'eval')
        super().__setitem__('timing', self.timing)

    @property
    def analyzer(self) -> str:
        return super().__getitem__('analyzer')

    @analyzer.setter
    def analyzer(self, analyzer: str):
        super().__setitem__('analyzer', analyzer)

    @property
    def analysis_result(self) -> AnalysisResult:
        return super().__getitem__('analysis_result')

    @analysis_result.setter
    def analysis_result(self, result: dict):
        super().__setitem__('analysis_result', result)

    @property
    def infile(self) -> str:
        return super().__getitem__('input_file')

    @infile.setter
    def infile(self, in_: str):
        super().__setitem__('input_file', in_)

    @property
    def outfile(self) -> Optional[str]:
        return super().__getitem__('out_file')

    @outfile.setter
    def outfile(self, in_: str):
        super().__setitem__('out_file', in_)

    def save(self) -> Result:
        """Saves results to file, if outfile is specified.
        If no outfile is specified, this method does nothing.

        Returns:
            A Result object.
        """
        if not self.outfile:
            return self
        dir_path, _ = os.path.split(self.outfile)
        if len(dir_path) > 0 and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(self.outfile, "w") as of:
            json.dump(self, of, indent=4)
        logger.info(f'Wrote to: {self.outfile}')
        return self

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

    def to_pretty(self) -> Result:
        Result.pretty_print(self.analysis_result)
        return self

    @staticmethod
    def pretty_print(result) -> None:
        """Displays neatly analysis results."""
        for cls in result.values():
            print(cls)


class AnalysisResult(dict):
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
        return f'{Colors.OKBLUE}{text}{Colors.ENDC}'


class ClassResult(AnalysisResult):
    """Stores analysis result of a single class."""

    def __init__(self, name: str, methods: dict[MethodResult]):
        super().__init__()
        self.update(methods)
        self.name = name

    def __str__(self):
        sep = "\n" + ('-' * self.LN_LEN) + '\n'
        c_name = self.coloring(self.name)
        items = map(str, self.values())
        return f'class {c_name}{sep}{sep.join(items)}'


class MethodResult(AnalysisResult):
    """Stores analysis result of a class method."""

    FLW_SEP = "🌢"

    def __init__(self, name: str, source: str, flows: list[list[str]],
                 variables: set[str]):
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


class Timeable(dict):

    def __init__(self, prt: dict, name: str):
        super().__init__()
        prt.__setitem__(name, self)

    def start(self):
        super().__setitem__('start', time.time_ns())

    def stop(self):
        end, start = time.time_ns(), super().__getitem__('start')
        super().__setitem__('end', end)
        super().__setitem__('ms', Timeable.millis(start, end))
        super().__setitem__('sec', Timeable.sec(start, end))

    @staticmethod
    def sec(start, end) -> float:
        return Timeable.measure(end, start, 1e9)

    @staticmethod
    def millis(start, end) -> float:
        return Timeable.measure(end, start, 1e6)

    @staticmethod
    def measure(start, end, units) -> float:
        return round((end - start) / units, 4)
