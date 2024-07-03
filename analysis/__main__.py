#!/usr/bin/env python3

import logging
import sys
from argparse import ArgumentParser, Namespace
from enum import Enum
from typing import Optional, Type

from . import Result, AbstractAnalyzer, JavaAnalyzer
from . import __version__, __title__ as prog_name


class Steps(Enum):
    PARSE = 'P'
    ANALYZE = 'A'
    EVALUATE = 'E'


def main():
    parser = ArgumentParser(prog=prog_name)
    args = __parse_args(parser)

    if not args.input:
        parser.print_help()
        sys.exit(1)

    logger = __logger_setup(args.log_level)
    result = Result(args.input, args.out, args.save)

    # noinspection PyPep8Naming
    MyAnalyzer = __choose_analyzer(args.input)
    if MyAnalyzer is None:
        logger.fatal('No supported analyzer')
        sys.exit(1)
    result.analyzer = MyAnalyzer.__name__
    logger.debug(f'Using {result.analyzer}')

    analyzer = MyAnalyzer(result)

    analyzer.parse(result.t_parse.start, result.t_parse.stop)
    if args.step == Steps.PARSE.value:
        return result.save()
    analyzer.analyze(result.t_analysis.start, result.t_analysis.stop)
    if args.step == Steps.ANALYZE.value:
        return result.to_pretty().save()
    logger.info('Evaluation not yet implemented!')
    return result.to_pretty().save()


def __choose_analyzer(input_file: str) \
        -> Optional[Type[AbstractAnalyzer]]:
    if JavaAnalyzer.lang_match(input_file):
        return JavaAnalyzer
    return None


def __logger_setup(level_arg: int) -> logging.Logger:
    level = [logging.FATAL, logging.ERROR, logging.WARNING,
             logging.INFO, logging.DEBUG][level_arg]
    root_log = logging.getLogger(prog_name)
    root_log.setLevel(level)
    fmt = '[%(asctime)s] %(levelname)s: %(message)s'
    formatter = logging.Formatter(fmt, datefmt='%H:%M:%S')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_log.addHandler(stream_handler)
    return root_log


# noinspection PyTypeChecker
def __parse_args(parser: ArgumentParser) -> Namespace:
    """Setup available program arguments."""
    parser.add_argument(
        'input',
        help='path to an input program file',
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
        metavar="X",
        dest='step',
        help='execution steps to run, '
             'P=parser only, A=analysis, E=evaluation '
             '(default: A)',
        default='A',
        type=str.upper
    )
    parser.add_argument(
        '-l',
        action='store',
        choices=range(0, 5),
        metavar="[0-4]",
        dest='log_level',
        help='logging info verbosity 0=min … 4=max',
        default=4,
        type=int
    )
    parser.add_argument(
        '--save',
        action='store_true',
        help='save analyzer results to a file'
    )
    return parser.parse_args(None)


if __name__ == '__main__':
    main()
