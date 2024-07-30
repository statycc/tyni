from types import SimpleNamespace
from typing import Optional

from pytest import raises

from analysis import Timeable, Result, ClassResult, AnalysisResult
from analysis import __main__
from analysis.analyzer import AbstractAnalyzer, choose_analyzer
from analysis.analyzer import JavaAnalyzer, JsonLoader


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


def my_chooser(input_file: str):
    return MockAnalyzer if \
        (input_file.endswith("java") or
         input_file.endswith("json")) else None


def my_isfile(path):
    return path and "." in path


def mock_setup(mocker, **args):
    mocker.patch('analysis.__main__.isfile', wraps=my_isfile)
    mocker.patch('analysis.__main__.choose_analyzer', wraps=my_chooser)
    mocker.patch('analysis.__main__.__parse_args',
                 return_value=(args := parse_args(**args)))
    return args


def test_chooser():
    assert choose_analyzer("my_file.java") == JavaAnalyzer
    assert choose_analyzer("result.json") == JsonLoader
    assert choose_analyzer("whatever.c") is None
    assert choose_analyzer("my_file.js") is None


def test_analyzes_file(mocker):
    mock_setup(mocker, input="my_file.java")
    assert isinstance(__main__.main(), Result)


def test_analyzes_exits_wo_input(mocker):
    args = mock_setup(mocker, input=None)
    assert args.input is None
    with raises(SystemExit):
        assert __main__.main()


def test_analyzes_exits_on_invalid_input(mocker):
    args = mock_setup(mocker, input="not_file")
    assert args.input is not None
    with raises(SystemExit):
        assert __main__.main()


def test_analyzes_exits_on_incompatible_input(mocker):
    args = mock_setup(mocker, input="some_file.c")
    assert args.input is not None
    assert my_isfile(args.input)
    with raises(SystemExit):
        assert __main__.main()


def test_printer_options(mocker):
    mock_setup(mocker, input="my.java", print="pretty=0, code = 0")
    printer = __main__.main().printer()
    assert printer.PRETTY is False
    assert printer.CODE is False
