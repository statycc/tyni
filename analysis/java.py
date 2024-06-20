from __future__ import annotations

import logging
import operator
import sys
from functools import reduce
from itertools import product
from typing import Type
from pprint import pprint

from antlr4 import FileStream, CommonTokenStream

from analysis import AbstractAnalyzer
from analysis.parser.JavaLexer import JavaLexer
from analysis.parser.JavaParser import JavaParser
from analysis.parser.JavaParserVisitor import JavaParserVisitor

logger = logging.getLogger(__name__)


class JavaAnalyzer(AbstractAnalyzer):

    @staticmethod
    def lang_match(f_name: str) -> bool:
        return f_name and f_name.endswith('.java')

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

    def analyze(self):
        assert self.tree
        result = ClassVisitor().visit(self.tree).result
        if self.out_file:
            self.save(result)
        else:
            pprint(result)
        return result


class ExtVisitor(JavaParserVisitor):
    def visit(self, tree):
        super().visit(tree)
        return self


class IdVisitor(ExtVisitor):
    """Finds identifiers in a parse tree"""

    def __init__(self):
        self.vars = {}

    def visitIdentifier(self, ctx: JavaParser.IdentifierContext):
        super().visitIdentifier(ctx)
        name = ctx.getText()
        self.vars[name] = name


class ClassVisitor(ExtVisitor):
    """Visits each class (possibly nested) and its methods."""

    def __init__(self, parent: ClassVisitor = None):
        self.parent = parent
        self.name = None
        self.result = {}

    def hierarchy(self, name):
        return name if not (self.parent and self.parent.name) else (
            '.'.join([self.parent.name, name]))

    @property
    def root(self):
        top = self
        while top.parent:
            top = top.parent
        return top

    @staticmethod
    def record(node, n, **kwargs):
        node.result[n] = {**kwargs}

    @staticmethod
    def mat_format(mat):
        return list(set(mat))

    @staticmethod
    def extract_text(ctx):
        token_source = ctx.start.getTokenSource()
        input_stream = token_source.inputStream
        start, stop = ctx.start.start, ctx.stop.stop
        return input_stream.getText(start, stop)

    def visitClassDeclaration(
            self, ctx: JavaParser.ClassDeclarationContext):
        self.name = self.hierarchy(ctx.identifier().getText())
        body = ctx.getChild(ctx.getChildCount() - 1)
        logger.debug(f'analyzing class {self.name}')
        result = ClassVisitor(parent=self).visit(body).result
        self.record(self.root, self.name, **result)

    def visitMethodDeclaration(
            self, ctx: JavaParser.MethodDeclarationContext):
        name = ctx.identifier().getText()
        logger.debug(f'analyzing method {name}')
        prog = RecVisitor().visit(ctx.methodBody())
        # noinspection PyTypeChecker
        self.record(self, name,
                    method=self.extract_text(ctx),
                    flows=self.mat_format(prog.matrix),
                    variables=list(prog.vars))


class RecVisitor(ExtVisitor):
    """Recursively process method body"""

    def __init__(self):
        # all encountered variables
        self.vars = {}
        self.out_v = {}
        self.matrix = []

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
        neq = lambda x: x[0] != x[1]
        return list(filter(neq, product(in_v, out_v)))

    @staticmethod
    def correction(occ, out):
        return RecVisitor.assign(occ, out)

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
        super().visitMethodCall(ctx)
        logger.warning(f'unhandled method call: {ctx.getText()}')

    def visitStatement(self, ctx: JavaParser.StatementContext):
        """Statement handlers, grammars/JavaParser.g4#L508"""
        # if ctx.blockLabel:
        #     logger.debug(f'block: {ctx.getText()}')
        # elif ctx.ASSERT():
        #     logger.debug(f'assert: {ctx.getText()}')
        if ctx.IF():
            return self.__if(ctx)
        elif ctx.FOR():
            return self.__for(ctx)
        elif ctx.WHILE():
            return self.__while(ctx)
        # elif ctx.DO():
        #     logger.debug(f'do while: {ctx.getText()}')
        # elif ctx.TRY():
        #     logger.debug(f'try: {ctx.getText()}')
        # elif ctx.SWITCH():
        #     logger.debug(f'switch: {ctx.getText()}')
        # elif ctx.SYNCHRONIZED():
        #     logger.debug(f'sync: {ctx.getText()}')
        # elif ctx.RETURN():
        #     logger.debug(f'return: {ctx.getText()}')
        # elif ctx.THROW():
        #     logger.debug(f'throw: {ctx.getText()}')
        # elif ctx.BREAK():
        #     logger.debug(f'break: {ctx.getText()}')
        # elif ctx.CONTINUE():
        #     logger.debug(f'cont: {ctx.getText()}')
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
        """Expressions, grammars/JavaParser.g4#L599"""
        if ctx.getChildCount() == 3:
            op = ctx.getChild(1).getText()
            # Identify assignment from operator form
            # if compound, out-variable is also an in-variable,
            # but such data flow is irrelevant for this analysis.
            if op in ['=', '+=', '-=', '*=', '/=', '%=', '&=',
                      '|=', '^=', '>>=', '>>>=', '<<=']:
                in_l, out_v = self.in_out_vars(ctx.getChild(0))
                in_v = self.in_vars(ctx.getChild(2))
                self.merge(self.vars, out_v, in_v, in_l)
                self.merge(self.out_v, out_v)
                fl1 = self.assign(in_v, out_v)
                fl2 = self.assign(in_l, out_v)
                self.matrix = self.compose(self.matrix, fl1, fl2)

        elif ctx.getChildCount() == 2:
            v1 = ctx.getChild(0).getText()
            v2 = ctx.getChild(1).getText()
            if v1 in ["++", "--"] or v2 in ["++", "--"]:
                in_l, out_v = self.in_out_vars(ctx.getChild(0))
                self.merge(self.vars, out_v, in_l)
                self.merge(self.out_v, out_v)
                flows = self.assign(in_l, out_v)
                self.matrix = self.compose(self.matrix, flows)
        else:
            super().visitExpression(ctx)

    @staticmethod
    def in_out_vars(ctx: JavaParser.ExpressionContext):
        all_vars = IdVisitor().visit(ctx).vars
        if len(all_vars) <= 1:
            return {}, all_vars
        # TODO: out exp with multiple variables
        #   is it always the case that left-most is out, rest are in?
        logger.debug(f"exp/L: {ctx.getText()} {ctx.getChildCount()}")
        logger.debug(f"exp/L: {ctx.getChild(0).getChildCount()}")
        return {}, {}

    @staticmethod
    def in_vars(ctx: JavaParser.ExpressionContext):
        return IdVisitor().visit(ctx).vars

    def corr_stmt(self, exp, body):
        ex_vars = self.occurs(exp)
        st_body = RecVisitor().visit(body)
        cr_mat = self.correction(ex_vars, st_body.out_v)
        self.matrix = self.compose(self.matrix, st_body.matrix, cr_mat)
        self.merge(self.vars, ex_vars, st_body.vars)
        self.merge(self.out_v, st_body.out_v)

    def __for(self, ctx: JavaParser.StatementContext):
        self.corr_stmt(ctx.getChild(2), ctx.getChild(4))

    def __if(self, ctx: JavaParser.StatementContext):
        self.corr_stmt(ctx.getChild(1), ctx.getChild(2))
        if ctx.getChildCount() > 4:  # else branch
            self.corr_stmt(ctx.getChild(1), ctx.getChild(4))

    def __while(self, ctx: JavaParser.StatementContext):
        self.corr_stmt(ctx.getChild(1), ctx.getChild(2))
