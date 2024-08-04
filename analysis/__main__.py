#!/usr/bin/env python3

import gc
import logging
import sys
from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from enum import Enum
from os.path import isfile, isdir, join as os_join
from sys import argv
from pathlib import Path

from . import Colors, utils, Evaluate, Result
from . import __version__, __title__ as prog_name
from .analyzer import choose_analyzer

Steps = Enum('Steps', [
    ('PARSE', 'P'), ('ANALYZE', 'A'), ('EVALUATE', 'E')])


# noinspection PyUnusedLocal
def main() -> Result:
    """Command-line interface main routine."""

    # parse the command arguments
    parser = ArgumentParser(
        prog=prog_name,
        formatter_class=RawTextHelpFormatter)
    args = __parse_args(parser)

    # make sure input file is specified
    if not args.input:
        parser.print_help()
        sys.exit(1)

    # setup logger utility
    logger = __logger_setup(args.log_level, (
        utils.log_filename(args.input, args.out)
        if args.log else None))

    def analyze_file(in_file):
        # initialize results objects
        result = Result(in_file, args.out, args.save, argv, args.print)
        # analyzer and solver setup
        # noinspection PyPep8Naming
        MyAnalyzer = choose_analyzer(in_file)
        if MyAnalyzer is None:
            logger.fatal('No supported analyzer')
            sys.exit(1)
        result.analyzer = MyAnalyzer.__name__
        result.solver = Evaluate.info()
        logger.debug(f'Using {result.analyzer}')

        # run the analyzer
        result.timers.total.start()
        analyzer = MyAnalyzer(result)
        analyzer.parse(result.timers.parse)
        if args.run == Steps.PARSE.value:
            result.timers.total.stop()
            return result.save()
        analyzer.analyze(result.timers.analysis)
        if args.run != Steps.ANALYZE.value:
            gc.collect()
            Evaluate(result).solve_all(result.timers.eval)
        result.timers.total.stop()
        result.save().to_pretty()
        return result

    # if input file does not exist,
    # print nice message to explain, then exit.
    if isfile(args.input):
        return analyze_file(args.input)
    elif isdir(args.input):
        all_files = [os_join(path) for path in
                     Path(args.input).rglob('*.*')]
        can_analyze = [f for f in all_files if choose_analyzer(f)]
        for fl in can_analyze:
            analyze_file(fl)
    else:
        logger.fatal(f'{Colors.FAIL}File does not exist: '
                     f'{args.input}{Colors.ENDC}')
        sys.exit(1)


def __logger_setup(level_arg: int, log_filename: str = None) \
        -> logging.Logger:
    """Setup logger.

    Arguments:
        level_arg: logger verbosity level
        log_filename: to write the log to a file

    Returns:
        A logger instance.
    """

    class __RemoveColorFilter(logging.Filter):
        """Removes color-characters from logger text."""

        def filter(self, record):
            if record and record.msg and \
                    isinstance(record.msg, str):
                record.msg = Colors.un_color(record.msg)
            return True

    level = [logging.FATAL, logging.ERROR, logging.WARNING,
             logging.INFO, logging.DEBUG][level_arg]
    root_log = logging.getLogger(prog_name)
    root_log.setLevel(level)
    fmt = u'[%(asctime)s] %(levelname)s: %(message)s'
    formatter = logging.Formatter(fmt, datefmt='%H:%M:%S')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_log.addHandler(stream_handler)
    if log_filename is not None:
        utils.ensure_path(log_filename)
        file_handler = logging.FileHandler(log_filename, mode='w')
        file_handler.addFilter(__RemoveColorFilter())
        file_handler.setFormatter(formatter)
        root_log.addHandler(file_handler)
    return root_log


# noinspection PyTypeChecker
def __parse_args(parser: ArgumentParser) -> Namespace:
    """Setup available program arguments."""
    parser.add_argument(
        'input',
        help='path to an input program or directory',
        nargs='?'
    )
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s ' + __version__,
    )
    parser.add_argument(
        '-o', '--out',
        action='store',
        dest='out',
        help='write output to FILE',
        metavar="FILE",
    )
    parser.add_argument(
        '-r', '--run',
        action='store',
        choices=[e.value for e in Steps],
        metavar="STEP",
        dest='run',
        help='analyzer steps\nP=parser, A=analysis, E=evaluation\n'
             '(default: E)',
        default='E',
        type=str.upper
    )
    parser.add_argument(
        '-p', '--print',
        action='store',
        dest='print',
        metavar="OPT",
        help='turn result printing options on=1 or off=0\n'
             'disable all printing output by "0"\n'
             '(default: "code=1,time=1")',
        type=str.upper
    )
    parser.add_argument(
        '-l',
        action='store',
        choices=range(0, 5),
        metavar="[0-4]",
        dest='log_level',
        help='logging verbosity 0=min … 4=max\n(default: 4)',
        default=4,
        type=int
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='save analyzer results to a file'
    )
    parser.add_argument(
        '--log',
        action='store_true',
        help='save logger output to a file'
    )
    return parser.parse_args(None)


if __name__ == '__main__':
    main()
