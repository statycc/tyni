# noinspection PyPackageRequirements
from z3 import Solver, Ints
from types import SimpleNamespace
import logging

logger = logging.getLogger(__name__)


class Evaluate:

    def __init__(self, analysis_result: dict):
        self.res = SimpleNamespace(**analysis_result)

    @property
    def classes(self):
        return self.res.result

    def methods(self, cls):
        return list(self.res.result[cls])

    def vars(self, cls, mhd):
        return list(self.res.result[cls][mhd]['variables'])

    def flows(self, cls, mhd):
        return list(self.res.result[cls][mhd]['flows'])

    def solve_all(self):
        for c in self.classes:
            for m in self.methods(c):
                vrs = tuple(self.vars(c, m))
                flows = self.flows(c, m)
                levels = {}
                if vrs:
                    Evaluate.solve(vrs, *flows, **levels)
                else:
                    logger.debug(f'{m} has no variables to evaluate')

    @staticmethod
    def solve(vrs, *flows, **levels):
        solver = Solver()

        # security levels are (positive) ints
        s_vars = Ints(' '.join(vrs))
        [solver.add(v >= 0) for v in s_vars]

        for (in_, out_) in flows:
            pass  # from Ints(in_) <= Ints(out_)
            # solver.add(s <= y)
            # solver.add(y <= z)

        # if levels are known
        # if isinstance(v1, int): solver.add(s == v1)
        # if isinstance(v2, int): solver.add(y == v2)
        # if isinstance(v3, int): solver.add(z == v3)

        sat_sol = str(solver.check())  # check sat/unsat
        if sat_sol == 'sat':
            sat_sol = str(solver.model()) + ' ' + sat_sol
        print(f'{sat_sol}')
