#!/usr/bin/env python3

import logging
import sys
from argparse import ArgumentParser, Namespace
from typing import Optional, Type

from src import __version__, __title__ as prog_name
from src import AbstractAnalyzer, JavaAnalyzer


def main():
    parser = ArgumentParser(prog=prog_name)
    args = __parse_args(parser)

    if not args.input:
        parser.print_help()
        sys.exit(1)

    log_levels = {
        '0': logging.FATAL,
        'v' * 1: logging.ERROR,
        'v' * 2: logging.WARNING,
        'v' * 3: logging.INFO,
        'v' * 4: logging.DEBUG}
    logger = __logger_setup(log_levels[args.log_level])

    # noinspection PyPep8Naming
    AnalyzerClass = __choose_analyzer(args.input)
    if AnalyzerClass is None:
        logger.fatal('No supported analyzer')
        sys.exit(1)
    logger.debug(f'Using {AnalyzerClass.__name__}')

    analyzer = AnalyzerClass(args.input, args.out)
    parsed = analyzer.parse()
    args.parse or parsed.analyze()


def __choose_analyzer(input_file: str) -> Optional[Type[AbstractAnalyzer]]:
    if JavaAnalyzer.lang_match(input_file):
        return JavaAnalyzer
    return None


def __logger_setup(level: int) -> logging.Logger:
    root_log = logging.getLogger(prog_name)
    root_log.setLevel(level)
    extras = ' %(module)s' if level == logging.DEBUG else ''
    fmt = f'[%(asctime)s] %(levelname)s{extras}: %(message)s'
    formatter = logging.Formatter(fmt, datefmt='%H:%M:%S')
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_log.addHandler(stream_handler)
    return root_log


def __parse_args(parser: ArgumentParser) -> Namespace:
    """Setup available program arguments."""
    parser.add_argument(
        'input',
        help='path to program file to analyze',
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
        help='file where to store analysis result',
    )
    parser.add_argument(
        '--parse',
        action='store_true',
        help='parse only without analysis'
    )
    parser.add_argument(
        '-l',
        action='store',
        choices=['0', 'v', 'vv', 'vvv', 'vvvv'],
        dest='log_level',
        help='logger verbosity: 0=min … vvvv=max',
        default='vvvv'
    )
    return parser.parse_args(None)


if __name__ == '__main__':
    main()
