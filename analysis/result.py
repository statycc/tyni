from __future__ import annotations
import json
import logging
import os
import time

logger = logging.getLogger(__name__)


class Result(dict):

    def __init__(self, in_: str, out_: str = None, save=False):
        super().__init__()
        self.infile = in_
        self.outfile = out_ or Result.default_out(self.infile) \
            if save else out_

        # init timers
        self.timing = {'parse': {}, 'analysis': {}, 'eval': {}}
        self.t_parse = Timeable(self.timing, 'parse')
        self.t_analysis = Timeable(self.timing, 'analysis')
        self.t_eval = Timeable(self.timing, 'eval')
        super().__setitem__('timing', self.timing)

    @property
    def analyzer(self):
        return super().__getitem__('analyzer')

    @analyzer.setter
    def analyzer(self, analyzer: str):
        super().__setitem__('analyzer', analyzer)

    @property
    def analysis_result(self):
        return super().__getitem__('analysis_result')

    @analysis_result.setter
    def analysis_result(self, result: dict):
        super().__setitem__('analysis_result', result)

    @property
    def infile(self):
        return super().__getitem__('input_file')

    @infile.setter
    def infile(self, in_: str):
        super().__setitem__('input_file', in_)

    @property
    def outfile(self):
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


class Timeable(dict):

    def __init__(self, prt: dict, name: str):
        super().__init__()
        prt.__setitem__(name, self)

    def start(self):
        super().__setitem__('start', time.time_ns())
        return self

    def stop(self):
        end, start = time.time_ns(), super().__getitem__('start')
        super().__setitem__('end', end)
        super().__setitem__('ms', Timeable.millis(start, end))
        super().__setitem__('s', Timeable.sec(start, end))
        return self

    @staticmethod
    def time_diff(start, end) -> int:
        return end - start

    @staticmethod
    def sec(start, end) -> float:
        return round(Timeable.time_diff(start, end) / 1e9, 1)

    @staticmethod
    def millis(start, end) -> float:
        return round(Timeable.time_diff(start, end) / 1e6, 1)
