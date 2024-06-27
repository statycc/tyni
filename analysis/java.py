from __future__ import annotations

import logging
import operator
import sys
from antlr4 import FileStream, CommonTokenStream
from functools import reduce
from itertools import product

from analysis import AbstractAnalyzer, ClassResult, MethodResult
from analysis import BaseVisitor
from analysis.parser.JavaLexer import JavaLexer
from analysis.parser.JavaParser import JavaParser
from analysis.parser.JavaParserVisitor import JavaParserVisitor

logger = logging.getLogger(__name__)


class JavaAnalyzer(AbstractAnalyzer):
    """Analyzer for Java programming language.

    Example:

    Parses and analyzes program, where program is some .java file.

    ```python
    JavaAnalyzer(program).parse().run()
    ```
    """

    @staticmethod
    def lang_match(input_file: str) -> bool:
        """Analyzes any file with .java extension.

        This is optimistic, since the grammar of the parser
        is Java-version specific.
        """
        return input_file.endswith('.java')

    def parse(self) -> JavaAnalyzer:
        """Attempt to parse the input file.

        This method terminates running process if parse fails.

        Raises:
            AssertionError: if input file is not analyzable.

        Returns:
            The analyzer.
        """
        assert JavaAnalyzer.lang_match(self.input_file)
        logger.debug(f'parsing {self.input_file}')
        input_stream = FileStream(
            self.input_file, encoding="UTF-8")
        lexer = JavaLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = JavaParser(stream)
        if parser.getNumberOfSyntaxErrors() > 0:
            return sys.exit(1)
        logger.debug("parsed successfully")
        self.tree = parser.compilationUnit()
        return self

    def run(self) -> dict:
        """Performs analysis on the input file.
        This requires parse has already been performed.

        Raises:
            AssertionError: if input has not been parsed successfully.

        Returns:
            A dictionary of analysis results.
        """
        assert self.tree
        result = ClassVisitor().visit(self.tree).result
        if self.out_file:
            self.save(result)
        else:
            self.pretty_print(result)
        return result


class ExtVisitor(BaseVisitor, JavaParserVisitor):
    """Shared behavior for all Java visitors."""

    def visit(self, tree):
        super().visit(tree)
        return self


class ClassVisitor(ExtVisitor):
    """Visits each class (possibly nested) and its methods."""

    def __init__(self, parent: ClassVisitor = None):
        self.parent: ClassVisitor = parent
        self.result: dict = {}
        self.name: str = ''

    def hierarchy(self, name):
        return name if not (self.parent and self.parent.name) \
            else ('.'.join([self.parent.name, name]))

    @property
    def root(self):
        top = self
        while top.parent:
            top = top.parent
        return top

    @staticmethod
    def record(node, n, data):
        node.result[n] = data

    @staticmethod
    def mat_format(mat):
        return list(set(mat))

    def visitClassDeclaration(
            self, ctx: JavaParser.ClassDeclarationContext):
        self.name = self.hierarchy(ctx.identifier().getText())
        body = ctx.getChild(ctx.getChildCount() - 1)
        logger.debug(f'class: {self.name}')
        result = ClassVisitor(parent=self).visit(body).result
        cls = ClassResult(self.name, result)
        self.record(self.root, self.name, cls)

    def visitMethodDeclaration(
            self, ctx: JavaParser.MethodDeclarationContext):
        name = ctx.identifier().getText()
        logger.debug(f'method: {name}')
        prog = RecVisitor().visit(ctx.methodBody())
        mat = self.mat_format(prog.matrix)
        mth = MethodResult(name, self.og_text(ctx), mat, prog.vars)
        # noinspection PyTypeChecker
        self.record(self, name, mth)


class RecVisitor(ExtVisitor):
    """Recursively process method body"""

    def __init__(self):
        self.vars = set()  # all encountered variables
        self.out_v = set()  # encountered out variables
        self.new_v = set()  # encountered declarations
        self.matrix: List[Tuple(str, str)] = []  # data flows (in, out)

    def subst(self, old_: str, new_: str):
        """Substitutes variable name in place.

        Arguments:
            old_: current name
            new_: the name after substitution.
        """
        # flake8: noqa: E731
        rename = lambda col: [new_ if v == old_ else v for v in col]
        self.matrix = [tuple(rename(pair)) for pair in self.matrix]
        self.vars = set(rename(self.vars))
        self.out_v = set(rename(self.out_v))
        self.new_v = set(rename(self.new_v))

    @staticmethod
    def merge(target: set, *args: set):
        [target.update(m) for m in args]

    @staticmethod
    def occurs(exp: JavaParser.ExpressionContext):
        return set(IdVisitor().visit(exp).vars)

    @staticmethod
    def compose(m1, *args):
        return reduce(operator.add, args, m1)

    @staticmethod
    def assign(in_v, out_v):
        return list(filter(
            lambda x: x[0] != x[1], product(in_v, out_v)))

    @staticmethod
    def correction(occ, out):
        return RecVisitor.assign(occ, out)

    @staticmethod
    def lvars(ctx: JavaParser.ExpressionContext) -> Tuple[set[str], set[str]]:
        """Find variables in an expression, with added knowledge that
        expression occurs on left-side of assignment, or in isolation.

        Returns:
            A pair of <in-variables, out-variables>
        """
        # find all variables in the expression
        all_vars = IdVisitor().visit(ctx)
        # the left-most is out, rest are in
        fst = all_vars.flat.pop(0)
        logger.debug(f'L/out: {fst}')
        if all_vars.flat:
            logger.debug(f'L/in:  {", ".join(all_vars.flat)}')
        return all_vars.vars, {fst}

    @staticmethod
    def rvars(ctx: JavaParser.ExpressionContext) -> set[str]:
        """Find variables in an expression, with added knowledge that
        expression occurs on right-side of assignment.

        The expression may contain const, variable, operation,
        method call, switch-exp, field access, object init,…etc.

        For now this assumes right-side only contains in variables,
        but perhaps that is not true (e.g., parametric method that
        returns, can have both in and out behavior, maybe.)

        Returns:
            Set of in-variables.
        """
        if (cc := ctx.getChildCount()) == 1:
            # base case / terminal
            if ctx.getChild(0).getChildCount() == 0:
                return RecVisitor.occurs(ctx)
            else:
                return RecVisitor.rvars(ctx.getChild(0))

        # unary
        elif cc == 2:
            c1, c2 = ctx.getChild(0), ctx.getChild(1)
            c1t, c2t = [x.getText() for x in (c1, c2)]
            # skip object inits with identifiers
            if c1t == "new":
                if RecVisitor.occurs(ctx):
                    RecVisitor.skipped(ctx, 'vars in')
                return set()
            u_ops = '++,--,!,~,+,-'.split(',')
            if c1t in u_ops or c2t in u_ops:
                id_node = c1 if c1t not in u_ops else c2
                return RecVisitor.rvars(id_node)
            # something else
            RecVisitor.skipped(ctx, 'rvars-2')
            return RecVisitor.occurs(ctx)

        # binary ops
        elif cc == 3:
            lc, op, rc = [ctx.getChild(n) for n in [0, 1, 2]]
            if (opt := op.getText()) == ".":
                return RecVisitor.rvars(lc)  # take leftmost
            # see JavaLexer L#155
            elif opt in '<,>,==,<=,>=,!=,&&,||,+,-,*,/,&,|,^,%'.split(','):
                return RecVisitor.rvars(lc) | RecVisitor.rvars(rc)
            elif lc.getText() == '(' and rc.getText() == ')':
                return RecVisitor.rvars(op)
            # something else
            RecVisitor.skipped(ctx, 'rvars-3')
            return RecVisitor.occurs(ctx)

        # ternary
        elif cc == 5:
            c0, c1, c2, c3, c4 = [ctx.getChild(n) for n in range(5)]
            if c1.getText() == "?" and c3.getText() == ":":
                return (RecVisitor.rvars(c0) | RecVisitor.rvars(c2) |
                        RecVisitor.rvars(c4))

        # min 4-part expressions: arrays and ???
        c1, cn = ctx.getChild(1), ctx.getChild(cc - 1)
        if c1.getText() == "[" and cn.getText() == "]":
            pass
        else:  # something else
            RecVisitor.skipped(ctx, f'rvars-{cc}')
        return RecVisitor.occurs(ctx)

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
        self.skipped(ctx, 'call')

    def visitVariableDeclarator(
            self, ctx: JavaParser.VariableDeclaratorContext):
        if (cc := ctx.getChildCount()) > 0:
            # left should only have out-vars
            out_v = self.occurs(ctx.getChild(0))
            self.merge(self.vars, out_v)
            self.merge(self.new_v, out_v)
            # decl with initialization
            if cc == 3 and ctx.getChild(1).getText() == '=':
                in_v = self.rvars(ctx.getChild(2))
                self.merge(self.vars, in_v)
                self.merge(self.out_v, out_v)
                flows = self.assign(in_v, out_v)
                self.matrix = self.compose(self.matrix, flows)
            return
        # fall-through
        self.skipped(ctx, 'decl')
        super().visitVariableDeclarator(ctx)

    def visitStatement(self, ctx: JavaParser.StatementContext):
        """Statement handlers cf. grammars/JavaParser.g4#L508"""
        if ctx.blockLabel:
            return super().visitStatement(ctx)
        elif ctx.ASSERT():
            return RecVisitor.skipped(ctx)
        elif ctx.IF():
            return self.__if(ctx)
        elif ctx.FOR():
            return self.__for(ctx)
        elif ctx.DO() and ctx.WHILE():
            return self.__do(ctx)
        elif ctx.WHILE():
            return self.__while(ctx)
        elif ctx.TRY():
            return RecVisitor.skipped(ctx)
        elif ctx.SWITCH():
            return self.__switch(ctx)
        elif ctx.SYNCHRONIZED():
            return RecVisitor.skipped(ctx)
        elif ctx.RETURN():
            return RecVisitor.skipped(ctx)
        elif ctx.THROW():
            return RecVisitor.skipped(ctx)
        elif ctx.BREAK():
            return RecVisitor.skipped(ctx)
        elif ctx.CONTINUE():
            return RecVisitor.skipped(ctx)
        elif ctx.YIELD():
            return RecVisitor.skipped(ctx)
        # elif ctx.SEMI():
        #     logger.debug(f'semi: {ctx.getText()}')
        # elif ctx.statementExpression:
        #     logger.debug(f'stmt_exp: {ctx.getText()}')
        # elif ctx.switchExpression():
        #     print("[!] switch expression")
        #     return self.__switch_exp(ctx)
        # elif ctx.identifierLabel:
        #     logger.debug(f'id_label: {ctx.getText()}')
        super().visitStatement(ctx)

    def visitExpression(self, ctx: JavaParser.ExpressionContext):
        """Expressions cf. grammars/JavaParser.g4#L599"""

        if (cc := ctx.getChildCount()) == 3:
            lc, o, rc = [ctx.getChild(n) for n in [0, 1, 2]]
            op = o.getText()
            # ASSIGNMENT: identify from operator form
            # if compound, out-variable is also an in-variable,
            # but such data flow is irrelevant for this analysis.
            if op in '=,+=,-=,*=,/=,%=,&=,|=,^=,>>=,>>>=,<<='.split(','):
                logger.debug(f'bop: {ctx.getText()}')
                in_l, out_v = self.lvars(lc)
                in_v = self.rvars(rc)
                logger.debug(f'R/in:  {", ".join(in_v) or "-"}')
                self.merge(self.vars, out_v, in_v, in_l)
                self.merge(self.out_v, out_v)
                flows = self.compose(
                    self.assign(in_v, out_v),
                    self.assign(in_l, out_v))
                self.matrix = self.compose(self.matrix, flows)
                return

            # DOT OPERATOR, e.g., System.out.println
            if op == ".":
                return self.skipped(ctx, 'dot-op')

        # UNARY incr/decr
        if cc == 2:
            c1, c2 = [ctx.getChild(n).getText() for n in [0, 1]]
            if c1 in ("++", "--") or c2 in ("++", "--"):
                logger.debug(f'unary: {ctx.getText()}')
                in_l, out_v = self.lvars(ctx)
                self.merge(self.vars, out_v, in_l)
                self.merge(self.out_v, out_v)
                flows = self.assign(in_l, out_v)
                self.matrix = self.compose(self.matrix, flows)
                return

        # METHOD CALL -> fall-through
        if cc == 1 and (c0 := ctx.getChild(0)).getChildCount() == 2:
            if (c1 := c0.getChild(1)).getChildCount() == 3:
                fst, lst = [c1.getChild(n).getText() for n in (0, 2)]
                if fst == '(' and lst == ')':
                    return super().visitExpression(ctx)

        # something else
        self.skipped(ctx, 'exp')
        super().visitExpression(ctx)

    def scoped_merge(self, child: RecVisitor):
        """Controlled merge when child has local scope."""
        # ensure variables in child scope are unique wrt. parent
        if dup := list(self.vars & child.new_v):
            for d_old in dup:
                d_new = self.uniq_name(d_old, self.vars)
                child.subst(d_old, d_new)
        # now safely merge scopes
        assert not self.vars & child.new_v
        self.merge(self.vars, child.vars)
        self.merge(self.out_v, child.out_v)
        self.merge(self.new_v, child.new_v)
        self.matrix = self.compose(self.matrix, child.matrix)
        return self

    @staticmethod
    def corr_stmt(
            exp: JavaParser.ExpressionContext,
            body: Optional[JavaParser.StatementContext] = None,
            visited: RecVisitor = None
    ) -> RecordVisitor:
        """Analyze body stmt and apply correction."""
        e_vars = RecVisitor.occurs(exp)
        stmt = visited or RecVisitor().visit(body)
        RecVisitor.merge(stmt.vars, e_vars)
        corr = RecVisitor.correction(e_vars, stmt.out_v)
        stmt.matrix = RecVisitor.compose(stmt.matrix, corr)
        return stmt

    def __if(self, ctx: JavaParser.StatementContext):
        cond = ctx.getChild(1)
        fst_branch = RecVisitor.corr_stmt(cond, ctx.getChild(2))
        if ctx.getChildCount() > 4:  # else branch
            snd_branch = RecVisitor.corr_stmt(cond, ctx.getChild(4))
            fst_branch.scoped_merge(snd_branch)
        self.scoped_merge(fst_branch)

    def __switch(self, ctx: JavaParser.StatementContext):
        cond, n_cases = ctx.getChild(1), ctx.getChildCount() - 1
        if (f_case := ctx.getChild(3)).getChildCount() == 2:
            lbl, body = f_case.getChild(0), f_case.getChild(1)
            stmt = RecVisitor.corr_stmt(cond, body)
            for cn in range(4, n_cases):
                cc = ctx.getChild(cn)
                lbl, body = cc.getChild(0), cc.getChild(1)
                BaseVisitor.skipped(body)

    def __switch_exp(self, ctx: JavaParser.StatementContext):
        print('switch exp kids', ctx.getChildCount())

    def __for(self, ctx: JavaParser.StatementContext):
        for_ctrl, body = ctx.getChild(2), ctx.getChild(4)

        # loop with 3-part control expression
        if for_ctrl.getChildCount() > 4:
            init, cond, updt = [for_ctrl.getChild(i) for i in [0, 2, 4]]
            stmt = RecVisitor().visit(init).visit(updt).visit(body)
            stmt = RecVisitor.corr_stmt(cond, visited=stmt)
            self.scoped_merge(stmt)
            return

        # foreach-style loop over an iterable
        if for_ctrl.getChildCount() == 1:
            cond = for_ctrl.getChild(0)
            iter_, src = cond.getChild(1), cond.getChild(3)
            stmt = RecVisitor.corr_stmt(iter_, body)
            # control also flows to iterator from iterable
            lc, rc = [self.occurs(x) for x in [iter_, src]]
            self.merge(stmt.vars, lc, rc)
            self.merge(stmt.new_v, lc)
            stmt.matrix = RecVisitor.compose(
                stmt.matrix, self.assign(rc, lc))
            self.scoped_merge(stmt)
            return

        self.skipped(ctx, 'for')
        super().visitStatement(ctx)

    def __while(self, ctx: JavaParser.StatementContext):
        cond, body = ctx.getChild(1), ctx.getChild(2)
        self.scoped_merge(RecVisitor.corr_stmt(cond, body))

    def __do(self, ctx: JavaParser.StatementContext):
        body, cond = ctx.getChild(1), ctx.getChild(3)
        self.scoped_merge(RecVisitor.corr_stmt(cond, body))


class IdVisitor(ExtVisitor):
    """Finds identifiers in a parse tree."""

    def __init__(self):
        # For some operations the order of discovery matters,
        # so maintain a list, to capture identifier order (L-R).
        self.flat = []

    @property
    def vars(self):
        return set(self.flat)

    def visitIdentifier(self, ctx: JavaParser.IdentifierContext):
        super().visitIdentifier(ctx)
        self.flat.append(ctx.getText())
