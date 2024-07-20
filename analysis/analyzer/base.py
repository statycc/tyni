from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Optional, Iterable

from analysis import Result, Timeable, AnalysisResult, Colors

logger = logging.getLogger(__name__)


class AbstractAnalyzer(ABC):
    def __init__(self, result: Result):
        """A base class for an analyzer.

        Arguments:
            result: Analysis results collector.
        """
        self._result = result
        self.tree = None

    @property
    def input_file(self) -> str:
        return self._result.infile

    @property
    def analysis_result(self) -> AnalysisResult:
        return self._result.analysis_result

    @analysis_result.setter
    def analysis_result(self, result: AnalysisResult):
        self._result.analysis_result = result

    @staticmethod
    def lang_match(input_file: str) -> bool:  # pragma: no cover
        """Determines if analyzer can handle input file.

        Arguments:
            input_file: input program to analyze.

        Returns:
            True is file seems analyzable.
        """
        return False

    @abstractmethod
    def parse(self, t: Optional[Timeable] = None) \
            -> AbstractAnalyzer:  # pragma: no cover
        """Parses the input file.

        Arguments:
            t: time-measuring utility

        Returns:
            The analyzer object.
        """
        pass

    @abstractmethod
    def analyze(self, t: Optional[Timeable] = None) \
            -> AbstractAnalyzer:  # pragma: no cover
        """Analyzes input file.

        Arguments:
            t: time-measuring utility

        Returns:
            The analysis results as a dictionary.
        """
        pass


class BaseVisitor(ABC):
    """Base class for a parse-tree visitor."""

    # noinspection PyMethodMayBeStatic
    def skipped(self, ctx, desc: str = "") -> None:
        """Displays a colored warning.

        Arguments:
            ctx: parse tree context.
            desc: optional description.
        """
        text = BaseVisitor.og_text(ctx)
        ctext = Colors.WARNING + text + Colors.ENDC
        desc_ = f" {desc}" if desc else ""
        logger.warning(f'unhandled{desc_} {ctext}')

    @staticmethod
    def og_text(ctx) -> str:
        """Get the original of a parse tree node.

        Arguments:
            ctx: tree node

        Returns:
            Node text with original whitespaces.
        """
        token_source = ctx.start.getTokenSource()
        input_stream = token_source.inputStream
        start, stop = ctx.start.start, ctx.stop.stop
        return input_stream.getText(start, stop)

    @staticmethod
    def uniq_name(init: str, known: Iterable[str]) -> str:
        """Find a unique replacement name for a variable.

        By "reverse pigeon-hole", this method always finds
        a unique name. The name is illegal in the input
        language, so that it is known, such name always
        came from renaming.

        Arguments:
            init: initial name.
            known: list of known names.

        Returns:
            A new name that is not in the known names.
        """
        for i in range(2, len(known) + 2 + 1):
            candidate = f'{init}{BaseVisitor.u_sub(i)}'
            if candidate not in known:
                return candidate

    @staticmethod
    def u_sub(n: int) -> str:
        """Unicode subscript of a positive int.

        Arguments:
            n: positive integer

        Returns:
            Same integer as text (in subscript).
        """
        assert n >= 0
        numbers = '₀,₁,₂,₃,₄,₅,₆,₇,₈,₉'.split(',')
        int_chars = [int(c) for c in str(n)]
        return ''.join([numbers[i] for i in int_chars])
