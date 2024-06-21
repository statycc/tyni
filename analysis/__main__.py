#!/usr/bin/env python3

import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import Optional, Type

from analysis import AbstractAnalyzer, JavaAnalyzer
from analysis import __version__, __title__ as prog_name


def main():
    parser = ArgumentParser(prog=prog_name)
    args = __parse_args(parser)

    if not args.input:
        parser.print_help()
        sys.exit(1)

    logger = __logger_setup(args.log_level)

    # noinspection PyPep8Naming
    AnalyzerClass = __choose_analyzer(args.input)
    if AnalyzerClass is None:
        logger.fatal('No supported analyzer')
        sys.exit(1)
    logger.debug(f'Using {AnalyzerClass.__name__}')

    analyzer = AnalyzerClass(args.input, args.out).parse()
    args.parse or analyzer.run()


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
        '--parse',
        action='store_true',
        help='parse only, skipping analysis'
    )
    return parser.parse_args(None)


if __name__ == '__main__':
    main()
