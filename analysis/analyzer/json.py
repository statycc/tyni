from __future__ import annotations

import json
import logging
from typing import Optional

from analysis import Timeable
from . import AbstractAnalyzer

logger = logging.getLogger(__name__)


class JsonLoader(AbstractAnalyzer):
    """Reloads a previous analysis result from a JSON file."""

    @staticmethod
    def lang_match(input_file: str) -> bool:
        """Accepts any file with .json extension."""
        return input_file.endswith('.json')

    def parse(self, t: Optional[Timeable] = None) -> JsonLoader:
        """Attempt to parse the input file."""
        logger.debug(f'parsing {self.input_file}')
        with open(self.input_file) as fl:
            self._result.reconstruct(json.load(fl))
        t.start().stop() if t else None
        logger.debug("parsed successfully")
        return self

    def analyze(self, t: Optional[Timeable] = None) -> JsonLoader:
        """Skipped."""
        t.start().stop() if t else None
        logger.debug("Reusing previous analysis result")
        return self
