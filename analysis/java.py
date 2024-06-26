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

    @staticmethod
    def lang_match(input_file: str) -> bool:
        return input_file.endswith('.java')

    def parse(self) -> JavaAnalyzer:
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
        assert self.tree
        result = ClassVisitor().visit(self.tree).result
        if self.out_file:
            self.save(result)
        else:
            self.pretty_print(result)
        return result


class ExtVisitor(BaseVisitor, JavaParserVisitor):
    def visit(self, tree):
        super().visit(tree)
        return self


class IdVisitor(ExtVisitor):
    """Finds identifiers in a parse tree"""

    def __init__(self):
        self.flat = []

    @property
    def vars(self):
        return dict([(x, x) for x in self.flat])

    def visitExpression(self, ctx: JavaParser.ExpressionContext):
        # if exp is a bin-op, and the op is dot-notation,
        # then process only the leftmost identifier.
        if (ctx.getChildCount() == 3 and
                ctx.getChild(1).getText() == '.'):
            self.visitExpression(ctx.getChild(0))
        else:
            super().visitExpression(ctx)

    def visitIdentifier(self, ctx: JavaParser.IdentifierContext):
        super().visitIdentifier(ctx)
        self.flat.append(ctx.getText())


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
        self.record(self.root, self.name,
                    ClassResult(self.name, result))

    def visitMethodDeclaration(
            self, ctx: JavaParser.MethodDeclarationContext):
        name = ctx.identifier().getText()
        logger.debug(f'method: {name}')
        prog = RecVisitor().visit(ctx.methodBody())
        # noinspection PyTypeChecker
        self.record(self, name, MethodResult(
            name, self.og_text(ctx),
            self.mat_format(prog.matrix),
            prog.vars))


class RecVisitor(ExtVisitor):
    """Recursively process method body"""

    def __init__(self):
        # all encountered variables
        self.vars = set()
        self.out_v = set()
        self.new_v = set()
        self.matrix = []

    def var_rename(self, old_, new_):
        # flake8: noqa: E731
        rename = lambda col: [new_ if v == old_ else v for v in col]
        self.matrix = [tuple(rename(pair)) for pair in self.matrix]
        self.vars = set(rename(self.vars))
        self.out_v = set(rename(self.out_v))
        self.new_v = set(rename(self.new_v))

    @staticmethod
    def merge(target, *args):
        [target.update(m) for m in args]

    @staticmethod
    def occurs(exp: JavaParser.ExpressionContext):
        return IdVisitor().visit(exp).vars

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
    def in_vars(ctx: JavaParser.ExpressionContext):
        return IdVisitor().visit(ctx).vars

    @staticmethod
    def in_out_vars(ctx: JavaParser.ExpressionContext):
        # find all variables in the expression
        all_vars = IdVisitor().visit(ctx)
        # the left-most is the out-variable
        fst = all_vars.flat.pop(0)
        # all others are in-variables
        rest = ', '.join(all_vars.flat)
        logger.debug(f'left out: {fst}')
        logger.debug(f'left in: {rest or "-"}')
        return all_vars.vars, {fst: fst}

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
        self.skipped(ctx, 'call')

    def visitVariableDeclarator(
            self, ctx: JavaParser.VariableDeclaratorContext):
        # declaration without init -> ignore
        if ctx.getChildCount() == 1:
            vid = self.in_vars(ctx.getChild(0))
            self.merge(self.vars, vid)
            self.merge(self.new_v, vid)
            return
        # declaration with initialization
        if ctx.getChildCount() == 3:
            # left should only have out-vars (no in-vars)
            out_v = self.in_vars(ctx.getChild(0))
            # TODO: RH could be an object, switch exp, etc.
            #  need more precision for handling here.
            in_v = self.in_vars(ctx.getChild(2))
            self.merge(self.vars, out_v, in_v)
            self.merge(self.out_v, out_v)
            self.merge(self.new_v, out_v)
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
        if ctx.ASSERT():
            return self.skipped(ctx)
        if ctx.IF():
            return self.__if(ctx)
        if ctx.FOR():
            return self.__for(ctx)
        if ctx.WHILE() and not ctx.DO():
            return self.__while(ctx)
        if ctx.WHILE() and ctx.DO():
            return self.__do(ctx)
            # elif ctx.TRY():
        #     logger.debug(f'try: {ctx.getText()}')
        # elif ctx.SWITCH():
        #     logger.debug(f'switch: {ctx.getText()}')
        elif ctx.SYNCHRONIZED():
            return self.skipped(ctx)
        elif ctx.RETURN():
            return self.skipped(ctx)
        elif ctx.THROW():
            return self.skipped(ctx)
        elif ctx.BREAK():
            return self.skipped(ctx)
        elif ctx.CONTINUE():
            return self.skipped(ctx)
        # elif ctx.YIELD():
        #     logger.debug(f'yield: {ctx.getText()}')
        # elif ctx.SEMI():
        #     logger.debug(f'semi: {ctx.getText()}')
        # elif ctx.statementExpression:
        #     logger.debug(f'stmt_exp: {ctx.getText()}')
        # elif ctx.switchExpression():
        #     logger.debug(f'switch_exp: {ctx.getText()}')
        # elif ctx.identifierLabel:
        #     logger.debug(f'id_label: {ctx.getText()}')
        super().visitStatement(ctx)

    def visitExpression(self, ctx: JavaParser.ExpressionContext):
        """Expressions cf. grammars/JavaParser.g4#L599"""
        # assignment
        if ctx.getChildCount() == 3:
            op = ctx.getChild(1).getText()
            # Identify assignment from operator form
            # if compound, out-variable is also an in-variable,
            # but such data flow is irrelevant for this analysis.
            if op in ['=', '+=', '-=', '*=', '/=', '%=', '&=',
                      '|=', '^=', '>>=', '>>>=', '<<=']:
                logger.debug(f'bop: {ctx.getText()}')
                in_l, out_v = self.in_out_vars(ctx.getChild(0))
                in_v = self.in_vars(ctx.getChild(2))
                self.merge(self.vars, out_v, in_v, in_l)
                self.merge(self.out_v, out_v)
                flows = self.compose(
                    self.assign(in_v, out_v),
                    self.assign(in_l, out_v))
                self.matrix = self.compose(self.matrix, flows)
                return

            # dot operator, e.g., System.out.println
            if op == ".":
                return self.skipped(ctx, 'dot-op')

        # unary incr/decr
        if ctx.getChildCount() == 2:
            ops = ["++", "--"]
            v1, v2 = ctx.getChild(0), ctx.getChild(1)
            if v1.getText() in ops or v2.getText() in ops:
                id_node = v1 if v1.getText() not in ops else v2
                logger.debug(f'unary: {ctx.getText()}')
                in_l, out_v = self.in_out_vars(id_node)
                self.merge(self.vars, out_v, in_l)
                self.merge(self.out_v, out_v)
                flows = self.assign(in_l, out_v)
                self.matrix = self.compose(self.matrix, flows)
                return

        # exp is a method call
        if ctx.getChildCount() == 1 \
                and ctx.getChild(0).getChildCount() == 2 \
                and ctx.getChild(0).getChild(1) \
                .getChildCount() == 3 \
                and ctx.getChild(0).getChild(1) \
                .getChild(0).getText() == '(' \
                and ctx.getChild(0).getChild(1) \
                .getChild(2).getText() == ')':
            # likely a method call -> continue
            return super().visitExpression(ctx)

        self.skipped(ctx, 'exp')
        super().visitExpression(ctx)

    def scoped_merge(self, child: RecVisitor):
        """Controlled merge of variables when child has local scope."""
        # ensure variables in child scope are unique wrt. parent
        if dup := list(self.vars & child.new_v):
            for d_old in dup:
                d_new = self.uniq_name(d_old, self.vars)
                child.var_rename(d_old, d_new)
        # now safely merge scopes
        assert not self.vars & child.new_v
        self.merge(self.vars, child.vars)
        self.merge(self.out_v, child.out_v)
        self.merge(self.new_v, child.new_v)
        self.matrix = self.compose(self.matrix, child.matrix)
        return self

    @staticmethod
    def corr_stmt(exp, body, pre_visited=None) -> RecordVisitor:
        """Applies expected correction."""
        ex_vars = RecVisitor.occurs(exp)
        stmt = pre_visited or RecVisitor().visit(body)
        RecVisitor.merge(stmt.vars, ex_vars)
        corr = RecVisitor.correction(ex_vars, stmt.out_v)
        stmt.matrix = RecVisitor.compose(stmt.matrix, corr)
        return stmt

    def __if(self, ctx: JavaParser.StatementContext):
        cond = ctx.getChild(1)
        fst_branch = RecVisitor.corr_stmt(cond, ctx.getChild(2))
        if ctx.getChildCount() > 4:  # else branch
            snd_branch = RecVisitor.corr_stmt(cond, ctx.getChild(4))
            fst_branch.scoped_merge(snd_branch)
        self.scoped_merge(fst_branch)

    def __for(self, ctx: JavaParser.StatementContext):
        for_ctrl, body = ctx.getChild(2), ctx.getChild(4)

        # C-style 3-part for loop
        if for_ctrl.getChildCount() > 4:
            init, cond, updt = [for_ctrl.getChild(i) for i in [0, 2, 4]]
            stmt = RecVisitor().visit(init).visit(updt).visit(body)
            stmt = RecVisitor.corr_stmt(cond, None, stmt)
            self.scoped_merge(stmt)
            return

        # foreach-style loop, over an iterable
        if for_ctrl.getChildCount() == 1:
            cond = for_ctrl.getChild(0)
            iter, src = cond.getChild(1), cond.getChild(3)
            stmt = RecVisitor.corr_stmt(iter, body)
            # control flow from iterable to iterator
            lc, rc = RecVisitor.occurs(iter), RecVisitor.occurs(src)
            self.merge(stmt.vars, lc, rc)
            self.merge(stmt.new_v, lc)
            stmt.matrix = RecVisitor.compose(
                stmt.matrix, self.assign(rc, lc))
            self.scoped_merge(stmt)
            return

        self.skipped(ctx, 'for')
        super().visitExpression(ctx)

    def __while(self, ctx: JavaParser.StatementContext):
        cond, body = ctx.getChild(1), ctx.getChild(2)
        loop_res = RecVisitor.corr_stmt(cond, body)
        self.scoped_merge(loop_res)

    def __do(self, ctx: JavaParser.StatementContext):
        body, cond = ctx.getChild(1), ctx.getChild(3)
        loop_res = RecVisitor.corr_stmt(cond, body)
        self.scoped_merge(loop_res)

