from __future__ import annotations

import json
import logging
import os
from abc import ABC, abstractmethod
from typing import Type

logger = logging.getLogger(__name__)


class AbstractAnalyzer(ABC):
    def __init__(self, input_file: str, out_file: str = None):
        self.input_file = input_file
        self.out_file = out_file or self.default_out(input_file)
        self.tree = None

    @staticmethod
    def lang_match(f_name: str) -> bool:
        """should return True is file seems analyzable"""
        return False

    @abstractmethod
    def parse(self) -> AbstractAnalyzer:
        """parses input file"""
        pass

    @abstractmethod
    def analyze(self) -> dict:
        """analyzes input file"""
        pass

    def save(self, data: dict) -> None:
        assert self.out_file
        content = {'input_prog': self.input_file, 'result': data}
        self.save_result(self.out_file, content)

    @staticmethod
    def default_out(input_file: str) -> str:
        file_only = os.path.splitext(input_file)[0]
        file_name = '_'.join(file_only.split('/')[1:])
        return os.path.join("output", f"{file_name}.json")

    @staticmethod
    def save_result(file_name: str, content: dict):
        dir_path, _ = os.path.split(file_name)
        if len(dir_path) > 0 and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        with open(file_name, "w") as outfile:
            json.dump(content, outfile, indent=4)
        logger.info(f'Wrote result to: {file_name}')
