from __future__ import annotations

import json
import logging
import os
import time
from typing import Optional, List, Tuple

from . import Colors, utils

logger = logging.getLogger(__name__)


class Result(dict):

    def __init__(self, in_: str, out_: str = None,
                 save=False, args=None):
        super().__init__()
        self.infile = in_
        self.outfile = out_ or (self.default_out(in_) if save else None)

        # init timers
        timing = {}
        super().__setitem__('timing', timing)
        self.t_parse = Timeable(timing, 'parsing', 1)
        self.t_analysis = Timeable(timing, 'analysis', 2)
        self.t_eval = Timeable(timing, 'evaluation', 3)
        self.timer = Timeable(timing, 'all-time', 4)

        if args:
            super().__setitem__('cmd', str(args))

    @property
    def analyzer(self) -> str:
        return super().__getitem__('analyzer')

    @analyzer.setter
    def analyzer(self, analyzer: str):
        super().__setitem__('analyzer', analyzer)

    @property
    def analysis_result(self) -> ClassResult:
        return super().__getitem__('analysis_result')

    @analysis_result.setter
    def analysis_result(self, result: ClassResult):
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
        utils.ensure_path(self.outfile)
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

    @property
    def log_fn(self):
        out_fn = self.outfile or self.default_out(self.infile)
        return out_fn[:-5] + ".log"

    def to_pretty(self) -> Result:
        times = sorted([self.__getattribute__(t) for t in
                        utils.attr_of(self, Timeable)],
                       key=Timeable.sort())
        times = '\n'.join([str(t) for t in times if str(t)]) \
                + AnalysisResult.SEP[:-1]
        parts = ['RESULTS', str(self.analysis_result), times]
        logger.info('\n'.join(parts))
        return self


class AnalysisResult(dict):
    """Base class for a capturing analysis results."""

    LN_LEN, PAD = 52, 8
    SEP = sep = "\n" + ('-' * LN_LEN) + '\n'

    @staticmethod
    def coloring(text: str) -> str:
        """Adds color to text.

        Arguments:
            text: text to color.

        Returns:
            The original text with added color.
        """
        return f'{Colors.OKCYAN}{text}{Colors.ENDC}'

    @staticmethod
    def bcolor(text: str) -> str:
        """Changes text to bold and colored.

        Arguments:
            text: text to color.

        Returns:
            The original text with added color.
        """
        ctext = AnalysisResult.coloring(text)
        return f'{Colors.BOLD}{ctext}{Colors.ENDC}'

    def children(self) -> List[str]:
        return list(self.keys())

    def children_of(self, key):
        return self.__getitem__(key) if key in self.keys() else None

    def __str__(self) -> str:
        """Neat display of analysis results."""
        return ''.join([str(cls) for cls in self.values()])


class ClassResult(AnalysisResult):
    """Stores analysis result of a single class."""

    def __init__(self, name: str, methods: dict[MethodResult]):
        super().__init__()
        self.update(methods)
        self.name = name

    def __str__(self):
        sep = self.SEP
        items = map(str, self.values())
        return f'{sep[1:]}{sep.join(items)}{sep[:-1]}' \
            if len(self.values()) > 0 else ''


class MethodResult(AnalysisResult):
    """Stores analysis result of a class method."""

    FLW_SEP = "🌢"

    def __init__(self, name: str, full_name: str,
                 source: str, flows: list[list[str]],
                 variables: set[str]):
        super().__init__()
        super().__setitem__('full_name', full_name)
        super().__setitem__('identifiers', list(variables))
        super().__setitem__('source', source)
        super().__setitem__('flows', flows)
        super().__setitem__('sat', None)
        super().__setitem__('model', None)
        self.name = name

    @property
    def full_name(self) -> str:
        return self.__getitem__('full_name')

    @property
    def ids(self) -> Tuple[str]:
        return tuple(self.__getitem__('identifiers'))

    @property
    def flows(self) -> List[str, str]:
        return self.__getitem__('flows')

    @property
    def source(self) -> str:
        return self.__getitem__('source')

    @property
    def sat(self) -> str:
        return self.__getitem__('sat')

    @sat.setter
    def sat(self, result: str):
        super().__setitem__('sat', result.upper())

    @property
    def model(self) -> str:
        return self.__getitem__('model')

    @model.setter
    def model(self, model):
        super().__setitem__('model', model)

    @staticmethod
    def flow_fmt(tpl):
        return f'{tpl[0]}{MethodResult.FLW_SEP}{tpl[1]}'

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
            vl = (0 if not acc else sp) + MethodResult.len_est(v)
            if acc + vl >= max_w:
                result.append(fst)
                fst, acc = [], 0
            acc, fst = acc + vl, fst + [v]
        return result + [fst]

    def join_(self, items, fmt=lambda x: x):
        # line length and left padding
        w, lpad = self.LN_LEN - self.PAD, self.PAD
        # item formatting function
        # separators for items and lines
        sep1, sep2 = ', ', '\n' + (' ' * lpad)
        # split into lines by length
        chunks = self.chunk(sorted(items), w, len(sep1))
        # format and join items in each line
        lines = [sep1.join(map(fmt, ch)) for ch in chunks]
        return sep2.join(lines) or '-'

    def __str__(self):
        name = self.bcolor(self.full_name)
        vars_ = self.join_(self.ids)
        flows = self.join_(self.flows, self.flow_fmt)
        model = self.join_(self.model.split(", ")) if self.sat else '-'
        has_eval = f' ==> {self.bcolor(self.sat)}' if self.sat else ''
        return (f'{self.source}\n'
                f'{"Method":<{self.PAD}}{name}{has_eval}\n'
                f'{"Vars":<{self.PAD}}{vars_}\n'
                f'{"Flows":<{self.PAD}}{flows}\n'
                f'{"Model":<{self.PAD}}{model}')


class Timeable(dict):

    def __init__(self, prt: dict, name: str, order=0):
        super().__init__()
        prt.__setitem__(name, self)
        self.name = name
        self.order = order

    def start(self):
        super().__setitem__('start', time.time_ns())

    def stop(self):
        end, start = time.time_ns(), super().__getitem__('start')
        super().__setitem__('end', end)
        super().__setitem__('ms', Timeable.millis(start, end))
        super().__setitem__('sec', Timeable.sec(start, end))

    def __bool__(self):
        return True

    @staticmethod
    def sort():
        return lambda x: x.order

    @staticmethod
    def sec(start, end) -> float:
        return Timeable.measure(start, end, 1e9)

    @staticmethod
    def millis(start, end) -> float:
        return Timeable.measure(start, end, 1e6)

    @staticmethod
    def measure(start, end, units) -> float:
        return round((end - start) / units, 6)

    def __str__(self):
        if 'end' not in self.keys():
            return ''
        s = round(super().__getitem__('sec'), 4)
        return f'{self.name:<{AnalysisResult.PAD * 2}} {s:>{10}} sec'
