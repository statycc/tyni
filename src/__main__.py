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
    logger_ = __logger_setup(log_levels[args.log_level])

    # noinspection PyPep8Naming
    AnalyzerClass = __get_analyzer(args.input)
    if AnalyzerClass is None:
        logger_.fatal('No supported analyzer')
        sys.exit(1)
    analyzer = AnalyzerClass(args.input, args.out)
    logger_.debug(f'Using {analyzer.__class__.__name__}')
    parsed = analyzer.parse()
    args.parse or parsed.analyze()


def __get_analyzer(input_file: str) -> Optional[Type[AbstractAnalyzer]]:
    if JavaAnalyzer.lang_match(input_file):
        return JavaAnalyzer
    return None


def __parse_args(parser: ArgumentParser) -> Namespace:
    """Setup available program arguments."""
    parser.add_argument(
        'input',
        help="path to program file to analyze",
        nargs="?"
    )
    parser.add_argument(
        '-o', '--out',
        action="store",
        dest="out",
        help="file where to store analysis result",
    )
    parser.add_argument(
        '-l',
        action="store",
        choices=['0', 'v', 'vv', 'vvv', 'vvvv'],
        dest="log_level",
        help="logger verbosity: 0=min … vvvv=max",
        default='vvvv'
    )
    parser.add_argument(
        "--parse",
        action='store_true',
        help="parse only without analysis"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s " + __version__,
    )
    return parser.parse_args(None)


def __logger_setup(level: int) -> logging.Logger:
    fmt = "[%(asctime)s] %(levelname)s (%(module)s): %(message)s"
    formatter = logging.Formatter(fmt, datefmt="%H:%M:%S")
    logger = logging.getLogger(prog_name)
    logger.setLevel(level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


if __name__ == '__main__':
    main()
