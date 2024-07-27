from __future__ import annotations

import json
import logging
import time
from typing import Optional, List, Tuple

from . import Colors, utils

logger = logging.getLogger(__name__)


class Result(dict):
    AR = 'analysis_result'

    def __init__(self, in_: str, out_: str = None,
                 save=False, args=None):
        super().__init__()
        self.cmd = args
        self.infile = in_
        self.outfile = out_ or (
            utils.gen_filename(in_) if save else None)
        self.timers = Timers()

    @property
    def analyzer(self) -> str:
        return self.__getitem__('analyzer')

    @analyzer.setter
    def analyzer(self, analyzer: str):
        self.__setitem__('analyzer', analyzer)

    @property
    def solver(self) -> str:
        return self.__getitem__('solver')

    @solver.setter
    def solver(self, solver):
        self.__setitem__('solver', solver)

    @property
    def analysis_result(self) -> ClassResult:
        return self.__getitem__(self.AR)

    @analysis_result.setter
    def analysis_result(self, result: ClassResult):
        self.__setitem__(self.AR, result)

    @property
    def infile(self) -> str:
        return self.__getitem__('input_file')

    @infile.setter
    def infile(self, in_: str):
        self.__setitem__('input_file', in_)

    @property
    def outfile(self) -> Optional[str]:
        return self.__getitem__('out_file')

    @outfile.setter
    def outfile(self, in_: str):
        self.__setitem__('out_file', in_)

    @property
    def cmd(self) -> str:
        return self.__getitem__('cmd')

    @cmd.setter
    def cmd(self, cmd: list[str]):
        self.__setitem__('cmd', " ".join(cmd or []))

    @property
    def timers(self) -> Timers:
        return self.__getitem__('timing')

    @timers.setter
    def timers(self, t: Timers):
        self.__setitem__('timing', t)

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

    def reconstruct(self, json_data: dict) -> Result:
        """Rebuild result object from JSON data.

        Arguments:
            json_data: a parsed json object of results.

        Returns:
            A re-initialized Result object.
        """
        out, tms = self.outfile, self.timers
        self.update(json_data)
        self.outfile, self.timers = out, tms
        self.analysis_result = ar = AnalysisResult()
        for k, v in json_data[self.AR].items():
            values = [(m, MethodResult.init(d))
                      for m, d in v.items()]
            ar[k] = ClassResult(k, dict(values))
        self.__setitem__('reloaded', True)
        return self

    @property
    def log_fn(self) -> str:
        """Generate default name for a log file."""
        return (self.outfile or utils.gen_filename(
            self.infile, depth=0)) + ".log "

    def to_pretty(self) -> Result:
        """Pretty-print analysis results."""
        logger.info('\n'.join([
            'RESULTS', str(self.analysis_result),
            str(self.timers), AnalysisResult.SL]))
        return self


class AnalysisResult(dict):
    """Base class for a capturing analysis results."""

    LLN, PAD = 52, 10
    SL = '-' * LLN
    SEP = f"\n{SL}\n"

    @property
    def not_empty(self):
        return len(self.values()) > 0

    @staticmethod
    def cyan_blue(text: str) -> str:
        return f'{Colors.OKCYAN}{text}{Colors.ENDC}'

    @staticmethod
    def yellow(text: str) -> str:
        return f'{Colors.WARNING}{text}{Colors.ENDC}'

    @staticmethod
    def bcolor(text: str) -> str:
        """Changes text to bold and colored.

        Arguments:
            text: text to color.

        Returns:
            The original text with added color.
        """
        ctext = AnalysisResult.cyan_blue(text)
        return f'{Colors.BOLD}{ctext}{Colors.ENDC}'

    def children(self) -> List[str]:
        return list(self.keys())

    def children_of(self, key):
        return self.__getitem__(key) if key in self.keys() else None

    def __str__(self) -> str:
        """Neat display of analysis results."""
        un_cov = f'{AnalysisResult.yellow("■")} = ' \
                 f'uncovered statements (if any)'
        return un_cov + '\n' + "".join(
            map(str, self.values()))


class ClassResult(AnalysisResult):
    """Stores analysis result of a single class."""

    def __init__(self, name: str, methods: dict[MethodResult]):
        super().__init__()
        self.update(methods)
        self.name = name

    def __str__(self):
        sep = self.SEP
        items = map(str, self.values())
        vals = f'{sep[1:]}{sep.join(items)}{sep[:-1]}'
        return vals if self.not_empty else ''


class MethodResult(AnalysisResult):
    """Stores analysis result of a method."""

    FLOW = "🌢"

    def __init__(self,
                 full_name: str,
                 source: str,
                 flows: list[list[str]],
                 identifiers: set[str],
                 skips: List[str] = None):
        super().__init__()
        super().__setitem__('full_name', full_name)
        super().__setitem__('source', source)
        super().__setitem__('flows', flows)
        super().__setitem__('identifiers', list(identifiers or {}))
        super().__setitem__('skips', skips or [])
        super().__setitem__('sat', None)
        super().__setitem__('model', None)
        super().__setitem__('smtlib', None)

    @staticmethod
    def init(data):
        empty = MethodResult(*((None,) * 5))
        empty.update(data)
        return empty

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
    def skips(self) -> List[str]:
        return self.__getitem__('skips')

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

    @property
    def smtlib(self) -> str:
        return self.__getitem__('smtlib')

    @smtlib.setter
    def smtlib(self, smt_lib):
        super().__setitem__('smtlib', smt_lib)

    @staticmethod
    def flow_fmt(tpl):
        return f'{tpl[0]}{MethodResult.FLOW}{tpl[1]}'

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
        w, lpad = self.LLN - self.PAD, self.PAD
        # item formatting function
        # separators for items and lines
        sep1, sep2 = ', ', '\n' + (' ' * lpad)
        # split into lines by length
        chunks = self.chunk(sorted(items), w, len(sep1))
        # format and join items in each line
        lines = [sep1.join(map(fmt, ch)) for ch in chunks]
        return sep2.join(lines) or '-'

    @staticmethod
    def map_skips(method: str, skips: List[str]) -> str:
        for skip in skips:
            method = method.replace(skip, MethodResult.yellow(skip))
        return method

    def __str__(self):
        source_code = self.map_skips(self.source, self.skips)
        name = self.bcolor(self.full_name)
        vars_ = self.join_(self.ids)
        flows = self.join_(self.flows, self.flow_fmt)
        model = self.join_(self.model.split(", ")) \
            if self.model else '-'
        return (f'{"METHOD:":<{self.PAD}}{name}\n'
                f'{source_code}\n'
                f'{"VARS:":<{self.PAD}}{vars_}\n'
                f'{"FLOWS:":<{self.PAD}}{flows}\n'
                f'{"MODEL:":<{self.PAD}}{self.sat}\n'
                f'{" " * self.PAD}{model}')


class Timers(dict):
    """Collection of timers."""

    def __init__(self):
        """Create all timers."""
        super().__init__()
        self.parse = Timeable(self, 'Parsing')
        self.analysis = Timeable(self, 'Analysis')
        self.eval = Timeable(self, 'Evaluation')
        self.total = Timeable(self, 'All-time')

    def all(self) -> List[Timeable]:
        """Get all timeable properties."""
        return sorted(map(
            self.__getattribute__,
            utils.attr_of(self, Timeable)),
            key=lambda x: x.order)

    def __str__(self) -> str:
        return '\n'.join(map(str, self.all()))


class Timeable(dict):
    """Abstract structure to track execution time.

    Internally it uses the Python standard library "time",
    and measure time in nanoseconds by UTC timestamp.
    Caller is responsible for starting and stopping timer.
    """

    def __init__(self, parent: dict, name: str):
        super().__init__()
        parent.__setitem__(name, self)
        self.order = len(parent.keys())
        self.name = name

    def reload(self, data: dict):
        """Re-loads timeable values."""
        self.update(data)

    @property
    def finished(self) -> bool:
        """True if timer has terminated."""
        return 'end' in self.keys()

    @property
    def t0(self) -> float:
        """Get start time."""
        return self.__getitem__('start')

    @property
    def t_sec(self) -> float:
        """Duration in seconds."""
        return round(self.__getitem__('sec'), 4)

    def __bool__(self) -> bool:
        """Timeable object is always non-falsy."""
        return True

    def start(self) -> Timeable:
        """Start timer."""
        self.__setitem__('start', time.time_ns())
        return self

    def stop(self) -> Timeable:
        """Stop timer."""
        end = time.time_ns()
        self.__setitem__('ms', self.diff(self.t0, end, 1e6))
        self.__setitem__('sec', self.diff(self.t0, end, 1e9))
        self.__setitem__('end', end)
        return self

    @staticmethod
    def diff(start: float, end: float, units: float) -> float:
        """Get time difference between start and end times.

        Arguments:
            start: start time, nanoseconds
            end: end time, nanoseconds
            units: divisor to adjust output units
        """
        return (end - start) / units

    def __str__(self) -> str:
        t = f' {self.t_sec:>10} sec' if self.finished else '-'
        return f'{self.name:<16}{t}'
