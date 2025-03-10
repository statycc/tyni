import os
import re
from typing import Any


def ensure_path(fn: str) -> None:
    """Make sure directory exists.

    Arguments:
        fn: filename
    """
    dir_path, _ = os.path.split(fn)
    if len(dir_path) > 0 and not os.path.exists(dir_path):
        os.makedirs(dir_path)


def trunc_name(fn: str, max_len: int) -> str:
    """Truncate file path for presentation.

    Argument:s
        fn: filename
        max_len: allowed max len.

    Returns:
       File name formatted to fit max len.
    """
    if len(fn) <= max_len:
        return fn
    pth = os.path.normpath(fn).split(os.path.sep)
    tmp, offset = pth[-1], -2
    while (t_len := len(tmp)) < max_len:
        nxt = pth[offset]
        if (len(nxt) + t_len + 1) < max_len:
            tmp = f'{nxt}/{tmp}'
            offset -= 1
        else:
            break
    return f'…/{tmp}'


def attr_of(obj: Any, type_: Any):
    """Get attributes of object that match type;
    e.g. get all str attributes of an object.

    Arguments:
        obj: the object to inspect
        type_: attributes type

    Returns:
        List of attribute names that match type.
    """
    return [x for x in dir(obj) if
            isinstance(getattr(obj, x), type_)]


def gen_filename(
        in_file: str, out_dir: str = 'out', depth: int = 3,
        ext: str = 'json') -> str:
    """Helper to generate output file name for input file.

    Arguments:
        in_file: program file path.
        out_dir: path to output directory [default:output].
        depth: number of directories to include in the generated
            filename, counting from end of in_file [default:3].
        ext: file extension [default: json].

    Returns:
        The generated file name.
    """
    file_only = (os.path.splitext(in_file)[0]).split('/')
    dir_depth = min(len(file_only), (depth + 1))  # +1 for the filename
    file_name = '_'.join(file_only[-dir_depth:])
    return os.path.join(out_dir, f"{file_name}.{ext}")


def log_filename(in_str: str, out_dir) -> str:
    """Generate default name for a log file."""
    return gen_filename(in_str, out_dir or 'out', depth=3, ext='log')


def rem_ws(txt: str) -> str:
    """Remove whitespace from text."""
    return re.sub('\\s+', " ", txt)


# noinspection PyClassHasNoInit,PyPep8Naming
class Bcolors:
    """Simple terminal coloring.
    credit: https://stackoverflow.com/a/287944"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def all_colors():
        """Get a list of all available colors.

        All colors <-> uppercase str class attributes
        """
        return [getattr(Bcolors, x) for x in
                attr_of(Bcolors, str) if x.isupper()]

    @staticmethod
    def un_color(text: str):
        """Remove all color codes from text."""
        for c in Bcolors.all_colors():
            text = text.replace(c, '')
        return text
