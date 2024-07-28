from __future__ import annotations

import logging
import operator
import sys
from functools import reduce
from itertools import product
from typing import Optional, Union, List, Tuple

from antlr4 import FileStream, CommonTokenStream

from analysis import AnalysisResult, ClassResult, MethodResult, Timeable
from analysis.parser import JavaLexer, JavaParser, JavaParserVisitor
from . import AbstractAnalyzer, BaseVisitor

logger = logging.getLogger(__name__)


class JavaAnalyzer(AbstractAnalyzer):
    """Analyzer for Java programming language.

    Example:

    Parses and analyzes a program where program is a .java file.

    ```python
    JavaAnalyzer(program).parse().analyze()
    ```
    """

    @staticmethod
    def lang_match(input_file: str) -> bool:
        """Analyzes any file with .java extension.

        This is optimistic, since the grammar recognized by
        the parser is Java-version specific.

        Arguments:
            input_file: the file to analyze.

        Returns:
            True is input file is compatible with this analyzer.
        """
        return input_file.endswith('.java')

    def parse(self, t: Optional[Timeable] = None) -> JavaAnalyzer:
        """Attempt to parse the input file.

        Arguments:
            t: timing utility

        Raises:
            AssertionError: if input file is not analyzable,
              because of file-extension mismatch.
            AssertionError: if input file cannot be parsed by
              the parser. The feedback here is not informative;
              so make sure to follow the grammar.

        Returns:
            The analyzer.
        """
        assert JavaAnalyzer.lang_match(self.input_file)
        logger.debug(f'parsing {self.input_file}')
        t.start() if t else None
        input_stream = FileStream(self.input_file, encoding="UTF-8")
        lexer = JavaLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = JavaParser(stream)
        t.stop() if t else None
        assert parser.getNumberOfSyntaxErrors() == 0
        logger.debug("parsed successfully")
        self.tree = parser.compilationUnit()
        return self

    def analyze(self, t: Optional[Timeable] = None) -> JavaAnalyzer:
        """Performs analysis on the input file.
        This requires parse has already been performed.

        Arguments:
            t: timing utility

        Raises:
            AssertionError: if input has not been parsed successfully.

        Returns:
            The analyzer.
        """
        assert self.tree
        t.start() if t else None
        self.analysis_result = ClassVisitor().visit(self.tree).result
        t.stop() if t else None
        logger.debug("Analysis phase completed")
        return self


class ExtVisitor(BaseVisitor, JavaParserVisitor):
    """Shared basic behavior for all Java visitors."""

    # unary operators
    U_OP = '++,--,!,~,+,-'.split(',')
    # operators JavaLexer L#155
    OP = '<,>,==,<=,>=,!=,&&,||,+,-,*,/,&,|,^,%'.split(',')

    def visit(self, tree: JavaParser.compilationUnit) -> ExtVisitor:
        super().visit(tree)
        return self

    @staticmethod
    def last(ctx: JavaParser.compilationUnit, n: int = 1) \
            -> Optional[JavaParser.compilationUnit]:
        """Access the context children indexing from the end.

        Arguments:
            ctx: parse tree context
            n: offset index where 1 gets the last child,
               2 get the second last child, etc.

        Returns:
            The n-th last child, if children exists, else None.
        """
        idx = max(0, (cc := ctx.getChildCount()) - n)
        return ctx.getChild(idx) if cc else None

    @staticmethod
    def is_array_exp(ctx: JavaParser.compilationUnit) -> bool:
        """Match array init and access patterns:
           1) identifier? ('[' ']')+
           2) identifier? ('[' expression ']')+ ('[' ']')*

        Arguments:
            ctx: parse tree compilation unit.

        Returns:
            True if the context matches pattern.
       """
        # need at minimum two children '[' and ']'
        if (cc := ctx.getChildCount()) >= 2:
            # skip first if not lbracket
            start = 0 if ctx.getChild(0).getText() == "[" else 1
            nodes = [ctx.getChild(i).getText()
                     for i in range(start, cc)]
            # still require min two children
            if (n := len(nodes)) < 2:
                return False
            # chunk nodes into len-3 triples
            exps = [nodes[(i * 3):(i * 3) + 3]
                    for i in range(0, n // 3)]
            # head is brackets containing expressions
            # => find first index where above is false
            split_idx = next(
                (i * 3 for (i, (l, _, r))
                 in enumerate(exps)
                 if (l, r) != ('[', ']')), n)
            # remaining tail, if any, must be [ ]-pairs
            pairs = nodes[split_idx:]
            return (len(pairs) % 2 == 0 and
                    all([node == ('[' if i % 2 == 0 else ']')
                         for i, node in enumerate(pairs)]))
        return False

    @staticmethod
    def is_array_init(ctx: JavaParser.compilationUnit) -> bool:
        """Array initialization pattern {…,…,…}."""
        return ((cc := ctx.getChildCount()) > 1 and
                ctx.getChild(0).getText() == '{' and
                ctx.getChild(cc - 1).getText() == '}' and
                ArrayInitializerVisitor().visit(ctx).match)


class ClassVisitor(ExtVisitor):

    def __init__(self, parent: ClassVisitor = None):
        """Top-level parse-tree visitor that visits each
        class, including nested and siblings, and methods.

        Arguments:
            parent: parent ClassVisitor, if any.
        """
        self.parent: ClassVisitor = parent
        self.result: AnalysisResult = AnalysisResult()
        self.name: str = ''

    def hierarchy(self, name: str) -> str:
        """Construct hierarchical name, traversing
        the parent classes.

        Arguments:
            name: name of current class.

        Returns:
            Full hierarchical name; for examples,
            class Prog { class Main { class Inner {}}}}
            returns "Prog.Main.Inner".
        """
        return (name if not (self.parent and self.parent.name)
                else ('.'.join([self.parent.name, name])))

    @property
    def root(self) -> ClassVisitor:
        """Gets the root-level ClassVisitor."""
        top = self
        while top.parent:
            top = top.parent
        return top

    def record(self, data: AnalysisResult) -> None:
        """Record analysis result.

        Arguments:
            data: analysis result.
        """
        node = (self.root if isinstance(data, ClassResult)
                else self)
        node.result[self.name] = data

    def to_result(self) -> ClassResult:
        """Converts self to a ClassResult instance."""
        return ClassResult(self.name, self.result)

    # noinspection PyTypeChecker
    def visitClassDeclaration(
            self, ctx: JavaParser.ClassDeclarationContext
    ) -> None:
        """Handler for visiting a class."""
        self.name = self.hierarchy(ctx.identifier().getText())
        cv, body = ClassVisitor(parent=self), ExtVisitor.last(ctx)
        logger.debug(f'class: {self.name}')
        self.record(cv.visit(body).to_result())

    def visitMethodDeclaration(
            self, ctx: JavaParser.MethodDeclarationContext
    ) -> None:
        """Handler for visiting a method."""
        self.name = ctx.identifier().getText()
        h, c = self.hierarchy(self.name), self.og_text(ctx)
        logger.debug(f'method: {self.name}')
        mth = RecVisitor().visit(ctx.methodBody())
        f, v, s = mth.flows, mth.vars, mth.skips
        self.record(MethodResult(h, c, f, v, s))


class RecVisitor(ExtVisitor):
    """Recursively process method body or its commands."""

    def __init__(self):
        self.vars = set()  # all encountered variables
        self.out_v = set()  # encountered out-variables
        self.new_v = set()  # encountered declarations
        self.matrix: List[Tuple[str, str]] = []  # data flows (in, out)
        self.skips: List[str] = []  # omitted statements

    @property
    def flows(self) -> List[Tuple[str, str]]:
        """Unique flow pairs."""
        return list(set(self.matrix))

    def skipped(self, ctx, desc: str = "") -> None:
        super().skipped(ctx, desc)
        self.skips += [BaseVisitor.og_text(ctx)]

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

    def lvars(self, ctx: JavaParser.ExpressionContext) \
            -> Tuple[set[str], set[str]]:
        """Find variables in an expression, with added knowledge that
        expression occurs on left-side of assignment -or- in isolation.

        Returns:
            A pair of <in-variables, out-variables>
        """
        if (cc := ctx.getChildCount()) == 0:
            return set(), set()

        elif cc == 1:  # terminal identifier
            if ctx.getChild(0).getChildCount() == 0:
                out_v = RecVisitor.occurs(ctx)
                logger.debug(f'L/out: {", ".join(out_v)}')
                return set(), out_v
            else:
                return self.lvars(ctx.getChild(0))

        elif cc == 2:  # standalone unary
            c1, c2 = ctx.getChild(0), ctx.getChild(1)
            c1t, c2t = [x.getText() for x in (c1, c2)]
            if c1t in self.U_OP or c2t in self.U_OP:
                id_node = c1 if c1t not in self.U_OP else c2
                return self.lvars(id_node)

        elif cc >= 4 and RecVisitor.is_array_exp(ctx):  # arrays
            all_vars = IdVisitor().visit(ctx)
            # the left-most is out, rest are in
            fst = all_vars.flat.pop(0)
            rest = all_vars.vars
            logger.debug(f'L/out: {fst}')
            logger.debug(f'L/in:  {", ".join(rest)}')
            return rest, {fst}

        # otherwise skip
        self.skipped(ctx)
        return set(), set()

    def rvars(self, ctx: JavaParser.ExpressionContext) -> set[str]:
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

        def default_handler():
            if in_v := RecVisitor.occurs(ctx):
                logger.debug(f'R/in:  {", ".join(in_v)}')
            return in_v

        if (cc := ctx.getChildCount()) == 0:
            return set()

        elif cc == 1:  # terminal identifiers, constants
            if ctx.getChild(0).getChildCount() == 0:
                return default_handler()
            else:
                return self.rvars(ctx.getChild(0))

        elif cc == 2:  # unary, new, method calls
            c1, c2 = ctx.getChild(0), ctx.getChild(1)
            c1t, c2t = [x.getText() for x in (c1, c2)]
            cn = c2.getChildCount()
            if c1t == "new":  # new object init
                return self.rvars(c2)
            # unary op
            if c1t in self.U_OP or c2t in self.U_OP:
                id_node = c1 if c1t not in self.U_OP else c2
                return self.rvars(id_node)
            if cn == 1 and c2t == '()':
                return self.rvars(c1)
            if (cn >= 3 and
                    c2.getChild(0).getText() == '(' and
                    c2.getChild(cn - 1).getText() == ')'):
                self.skipped(ctx, 'call/block:')
                return set()
            # array exp/initialization
            if (cn >= 3 and c2.getChild(0).getText() == '[' and
                    (c2.getChild(cn - 1).getText() == ']' or
                     c2.getChild(cn - 2).getText() == ']')):
                return self.rvars(c1) | set(reduce(set.union, map(
                    self.rvars, c2.children)))

            # something else
            self.skipped(ctx, 'rvars-2')
            return default_handler()

        elif self.is_array_init(ctx):
            chd = map(ctx.getChild, range(1, cc, 2))
            return set(reduce(set.union, map(self.rvars, chd)))

        elif cc == 3:  # binary ops
            lc, op, rc = [ctx.getChild(n) for n in [0, 1, 2]]
            if (opt := op.getText()) == ".":
                self.skipped(ctx, 'dot-op')
                return set()
            elif opt in self.OP:
                return self.rvars(lc) | self.rvars(rc)
            # block statement
            elif lc.getText() == '(' and rc.getText() == ')':
                return self.rvars(op)
            # something else
            self.skipped(ctx, 'rvars-3')
            return default_handler()

        elif cc == 5:
            c0, c1, c2, c3, c4 = [ctx.getChild(n) for n in range(5)]
            # ternary operation
            if c1.getText() == "?" and c3.getText() == ":":
                return self.rvars(c0) | self.rvars(c2) | self.rvars(c4)

        if ctx.getChild(0).getText() == "switch":  # switch expression
            # TODO: can there be new out vars?
            #   Yes, e.g. a switch expression
            vst = RecVisitor().visit(ctx)
            logger.debug(f'R/in:  {", ".join(vst.vars)}')
            return vst.vars

        if RecVisitor.is_array_exp(ctx):  # array accesses
            return default_handler()

        # something else
        self.skipped(ctx, f'rvars-{cc}')
        return default_handler()

    def xvars(self, ctx: JavaParser.ExpressionContext) -> set[str]:
        """Find variables in an expression, with added knowledge that
        input is a boolean expression.

        Returns:
            Set of occurring variables.
        """
        if (cc := ctx.getChildCount()) == 3:  # binary ops
            lc, op, rc = [ctx.getChild(n) for n in [0, 1, 2]]
            if lc.getText() == '(' and rc.getText() == ')':
                return self.xvars(op)
            # Java-style equality comparison: a.equals(b)
            # => ignore the equals identifier
            if ((op.getText()) == "." and rc.getChildCount() == 2 and
                    rc.getChild(0).getText() == 'equals'):
                return self.xvars(lc) | self.xvars(rc.getChild(1))
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
        """
        Statement handlers matching grammar.
        cf. grammars/JavaParser.g4#L508--528
        """
        if ctx.blockLabel:
            return super().visitStatement(ctx)
        elif ctx.ASSERT():
            return self.skipped(ctx)
        elif ctx.IF():
            return self.__if(ctx)
        elif ctx.FOR():
            return self.__for(ctx)
        elif ctx.DO() and ctx.WHILE():
            return self.__do(ctx)
        elif ctx.WHILE():
            return self.__while(ctx)
        elif ctx.TRY():
            return self.skipped(ctx)
        elif ctx.SWITCH():
            return self.__switch(ctx)
        elif ctx.SYNCHRONIZED():
            return self.skipped(ctx)
        elif ctx.RETURN():
            return self.skipped(ctx)
        elif ctx.THROW():
            return self.skipped(ctx)
        elif ctx.BREAK():
            return
        elif ctx.CONTINUE():
            return
        elif ctx.YIELD():
            return self.skipped(ctx)
        elif ctx.SEMI():
            return super().visitStatement(ctx)
        elif ctx.statementExpression:
            return super().visitStatement(ctx)
        elif ctx.switchExpression():
            return super().visitStatement(ctx)
        elif ctx.identifierLabel:
            return super().visitStatement(ctx)
        assert False  # should not occur

    def visitExpression(self, ctx: JavaParser.ExpressionContext):
        """Expressions cf. grammars/JavaParser.g4#L599--660"""
        if (cc := ctx.getChildCount()) == 3:
            lc, o, rc = [ctx.getChild(n) for n in [0, 1, 2]]
            op = o.getText()
            # ASSIGNMENT: identify from operator form
            # if compound, out-variable is also an in-variable,
            # but such data flow is irrelevant for this analysis.
            if op in '=,+=,-=,*=,/=,%=,&=,|=,^=,>>=,>>>=,<<=' \
                    .split(','):
                logger.debug(f'bop: {ctx.getText()}')
                in_l, out_v = self.lvars(lc)
                in_v = self.rvars(rc)
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

        if cc == 1 and len(ct := ctx.getText()):
            # numeric, string constants
            if ct.isdecimal(): return
            if ct[0] == '"' and ct[-1] == '"': return

        # something else
        self.skipped(ctx, f'exp {ctx.getChildCount()}')
        super().visitExpression(ctx)

    def visitSwitchExpression(
            self, ctx: JavaParser.SwitchExpressionContext):
        """It's a fancy switch."""
        return self.__switch(ctx)

    def visitSwitchLabel(self, ctx: JavaParser.SwitchLabelContext):
        """Ignore case labels."""
        return

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

    def corr_stmt(
            self,
            exp: JavaParser.ExpressionContext,
            body: Optional[JavaParser.StatementContext] = None,
            visited: RecVisitor = None
    ) -> RecVisitor:
        """Analyze body stmt and apply correction."""
        e_vars = self.xvars(exp)
        stmt = visited or RecVisitor().visit(body)
        RecVisitor.merge(stmt.vars, e_vars)
        corr = RecVisitor.correction(e_vars, stmt.out_v)
        stmt.matrix = RecVisitor.compose(stmt.matrix, corr)
        return stmt

    def __if(self, ctx: JavaParser.StatementContext):
        cond = ctx.getChild(1)
        fst_branch = self.corr_stmt(cond, ctx.getChild(2))
        if ctx.getChildCount() > 4:  # else branch
            snd_branch = self.corr_stmt(cond, ctx.getChild(4))
            fst_branch.scoped_merge(snd_branch)
        self.scoped_merge(fst_branch)

    def __switch(
            self, ctx: Union[JavaParser.StatementContext |
                             JavaParser.SwitchExpressionContext]):
        switch_ctx, switch_var = RecVisitor(), ctx.getChild(1)
        # iterate cases
        for cn in range(3, ctx.getChildCount() - 1):
            case = RecVisitor()
            for body_st in ctx.getChild(cn).children:
                case.visit(body_st)
            switch_ctx.scoped_merge(case)
        stmt = self.corr_stmt(switch_var, visited=switch_ctx)
        self.scoped_merge(stmt)

    def __for(self, ctx: JavaParser.StatementContext):
        for_ctrl, body = ctx.getChild(2), ctx.getChild(4)

        # loop with 3-part control expression
        if for_ctrl.getChildCount() > 4:
            init, cond, updt = [for_ctrl.getChild(i) for i in [0, 2, 4]]
            stmt = RecVisitor().visit(init).visit(updt).visit(body)
            stmt = self.corr_stmt(cond, visited=stmt)
            self.scoped_merge(stmt)
            return

        # foreach-style loop over an iterable
        if for_ctrl.getChildCount() == 1:
            cond = for_ctrl.getChild(0)
            iter_, src = cond.getChild(1), cond.getChild(3)
            stmt = self.corr_stmt(iter_, body)
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
        self.scoped_merge(self.corr_stmt(cond, body))

    def __do(self, ctx: JavaParser.StatementContext):
        body, cond = ctx.getChild(1), ctx.getChild(3)
        self.scoped_merge(self.corr_stmt(cond, body))


class IdVisitor(ExtVisitor):
    """Finds identifiers in a parse tree."""

    def __init__(self):
        # For some operations the order of discovery matters,
        # so maintain a list to capture identifier order (L-R).
        self.flat = []

    @property
    def vars(self):
        return set(self.flat)

    def visitIdentifier(self, ctx: JavaParser.IdentifierContext):
        super().visitIdentifier(ctx)
        self.flat.append(ctx.getText())


class ArrayInitializerVisitor(ExtVisitor):

    def __init__(self):
        self.match = False

    def visitArrayInitializer(
            self, ctx: JavaParser.ArrayInitializerContext):
        self.match = True
