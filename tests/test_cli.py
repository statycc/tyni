import sys
from types import SimpleNamespace
from typing import Optional

from pytest import raises

from analysis import Timeable, ClassResult, AnalysisResult, __main__
from analysis.analyzer import AbstractAnalyzer


class MockAnalyzer(AbstractAnalyzer):

    def parse(self, t: Optional[Timeable] = None):
        return self

    def analyze(self, t: Optional[Timeable] = None):
        self.analysis_result = ClassResult("Dummy", AnalysisResult())
        return self


def parse_args(**kwargs):
    default = {'input': None, 'out': None,
               'run': 'E', 'save': False, 'print': '',
               'log': False, 'log_level': 4}
    return SimpleNamespace(**dict({**default, **kwargs}))


def my_isfile(arg):
    return arg is not None


def mock_setup(mocker, **args):
    mocker.patch('analysis.__main__.isfile', wraps=my_isfile)
    mocker.patch('analysis.__main__.__parse_args',
                 return_value=(args := parse_args(**args)))
    mocker.patch('analysis.__main__.choose_analyzer',
                 return_value=MockAnalyzer)
    return args


def test_analyzes_file(mocker):
    args = mock_setup(mocker, input="my_file.java")
    assert args.input is not None
    assert __main__.main() is not None


def test_analyzes_exits_on_no_file(mocker):
    args = mock_setup(mocker, input=None)
    assert args.input is None
    with raises(SystemExit):
        assert __main__.main()


def test_printer_options(mocker):
    mock_setup(mocker, input="my.java", print="pretty=0, code = 0")
    printer = __main__.main().printer()
    assert printer.PRETTY is False
    assert printer.CODE is False
