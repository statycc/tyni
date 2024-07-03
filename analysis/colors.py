from . import utils


# noinspection PyClassHasNoInit,PyPep8Naming
class Bcolors:
    """From https://stackoverflow.com/a/287944"""
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
        """All colors <-> uppercase str attributes"""
        return [getattr(Bcolors, x) for x in
                utils.attr_of(Bcolors, str) if x.isupper()]

    @staticmethod
    def un_color(s: str):
        """removes all color codes from text"""
        for c in Bcolors.all_colors():
            s = s.replace(c, '')
        return s
