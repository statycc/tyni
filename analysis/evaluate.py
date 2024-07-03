# noinspection PyPackageRequirements
import logging
from typing import Optional

from z3 import Solver, Ints

from . import Result, AnalysisResult, MethodResult, Timeable

logger = logging.getLogger(__name__)


class Evaluate:

    def __init__(self, result: Result):
        self.result = result

    @property
    def ar(self) -> AnalysisResult:
        return self.result.analysis_result

    def solve_all(self, t: Optional[Timeable] = None):
        cls_methods = [j for sub in [[
            (c, m) for m in self.ar.children_of(c).keys()
            if self.ar[c][m].ids]
            for c in self.ar.children()] for j in sub]
        logger.debug(f'Methods to evaluate: {len(cls_methods)}')

        t.start() if t else None
        for (cls, m_name) in cls_methods:
            method = self.ar[cls][m_name]
            logger.debug(f'Evaluating {cls}.{m_name}')
            Evaluate.solve(method)
        t.stop() if t else None
        logger.debug("Evaluation completed")

    # noinspection PyPep8Naming
    @staticmethod
    def solve(method: MethodResult, **levels):

        solver = Solver()
        vrs, flows = method.ids, method.flows
        s_vars = Ints(' '.join([f'l({v})' for v in vrs]))

        # security levels are (positive) ints
        [solver.add(v >= 0) for v in s_vars]

        # add flow constraints
        for (in_, out_) in flows:
            idx1, idx2 = vrs.index(in_), vrs.index(out_)
            inInt, outInt = s_vars[idx1], s_vars[idx2]
            solver.add(inInt <= outInt)

        # if levels are known
        for v_name, level in levels.items():
            vInt = s_vars[vrs.index(v_name)]
            solver.add(vInt == level)

        # check sat/unsat
        sat_sol = method.sat = str(solver.check())
        if sat_sol == 'sat':
            method.model = str(solver.model())[1:-1] \
                .replace(' = ', '=').replace('\n', '')
