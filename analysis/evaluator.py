from z3 import Solver, Ints


class Evaluate:

    def __init__(self, result):
        self.result = result

    @staticmethod
    def solve(variables, **levels):
        solver = Solver()
        (s, y, z) = Ints('s y z')

        # levels are nats
        solver.add(s >= 0)
        solver.add(y >= 0)
        solver.add(z >= 0)

        # from matrix:
        solver.add(s <= y)
        solver.add(y <= z)

        # if levels are known
        if isinstance(v1, int): solver.add(s == v1)
        if isinstance(v2, int): solver.add(y == v2)
        if isinstance(v3, int): solver.add(z == v3)

        problem = f's={v1}, y={v2}, z={v3}'
        sat_sol = str(solver.check())  # check sat/unsat
        if sat_sol == 'sat':
            sat_sol += ' ' + str(solver.model())
        print(f'{problem:25} {sat_sol}')
