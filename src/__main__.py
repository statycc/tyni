#!/usr/bin/env python3

import json
import logging
import os
import sys
from itertools import product

from antlr4 import FileStream, CommonTokenStream

from src import JavaLexer, JavaParser, JavaParserVisitor


def setup_logger(logger_id, level: int = logging.DEBUG):
    fmt = "[%(asctime)s] %(levelname)s: %(message)s"
    formatter = logging.Formatter(fmt, datefmt="%H:%M:%S")
    logger_ = logging.getLogger(logger_id)
    logger_.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger_.addHandler(stream_handler)
    return logger_


logger = setup_logger(__name__)


def analyze(input_file, out_file):
    input_stream = FileStream(input_file)
    lexer = JavaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JavaParser(stream)
    if parser.getNumberOfSyntaxErrors() > 0:
        logger.error("syntax errors")
    else:
        tree = parser.compilationUnit()
        methods = MethodVisitor().visit(tree)
        data = {'input_prog': input_file, 'result': methods.result}
        save_result(out_file, data)


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


class MethodVisitor(ExtVisitor):
    """Visits each class method"""

    def __init__(self):
        self.result = {}

    def record(self, n, **kwargs):
        self.result[n] = {**kwargs}

    @staticmethod
    def mat_format(mat):
        return list(set(mat))

    @staticmethod
    def extract_text(ctx):
        token_source = ctx.start.getTokenSource()
        input_stream = token_source.inputStream
        start, stop = ctx.start.start, ctx.stop.stop
        return input_stream.getText(start, stop)

    def visitMethodDeclaration(
            self, ctx: JavaParser.MethodDeclarationContext):
        ret_type = ctx.typeTypeOrVoid().getText()
        name = ctx.identifier().getText()
        body = ctx.methodBody()
        b_visit = RecVisitor().visit(body)
        self.record(
            name,
            method_input=self.extract_text(ctx),
            return_type=ret_type,
            variables=list(b_visit.vars),
            flows=self.mat_format(b_visit.matrix))


class RecVisitor(ExtVisitor):
    """Recursively process method body"""

    def __init__(self):
        # all encountered variables
        self.vars = {}
        self.in_v = {}
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
        for m2 in args:
            m1 = m1 + m2
        return m1

    @staticmethod
    def assign(in_v, out_v):
        tmp = list(product(in_v, out_v))
        return list(filter(lambda x: x[0] != x[1], tmp))

    @staticmethod
    def correction(occ, out):
        return RecVisitor.assign(occ, out)

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
        super().visitMethodCall(ctx)
        logger.warning(f'skipped method call: {ctx.getText()}')

    def visitStatement(self, ctx: JavaParser.StatementContext):
        """Statement handlers, grammars/JavaParser.g4#L508"""
        # if ctx.blockLabel:
        #     logger.debug(f'block: {ctx.getText()}')
        # elif ctx.ASSERT():
        #     logger.debug(f'assert: {ctx.getText()}')
        if ctx.IF():
            return self.__if(ctx)
        # elif ctx.FOR():
        #     logger.debug(f'for: {ctx.getText()}')
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
            if op == '=':
                out_v = IdVisitor().visit(ctx.getChild(0)).vars
                in_v = IdVisitor().visit(ctx.getChild(2)).vars
                self.merge(self.vars, out_v, in_v)
                self.merge(self.in_v, in_v)
                self.merge(self.out_v, out_v)
                flows = self.assign(in_v, out_v)
                self.matrix = self.compose(self.matrix, flows)
            elif op in ['+=', '-=', '*=', '/=', '&=', '|=',
                        '^=', '>>=', '>>>=', '<<=', '%=']:
                logger.warning("TODO:", op)
        elif ctx.getChildCount() == 2:
            v1 = ctx.getChild(0).getText()
            v2 = ctx.getChild(1).getText()
            if v1 in ['++', '--'] or v2 in ['++', '--']:
                in_v = out_v = IdVisitor().visit(ctx).vars
                self.merge(self.vars, in_v)
                self.merge(self.in_v, in_v)
                self.merge(self.out_v, out_v)
        else:
            super().visitExpression(ctx)

    def corr_stmt(self, exp, body):
        ex_vars = self.occurs(exp)
        st_body = RecVisitor().visit(body)
        cr_mat = self.correction(ex_vars, st_body.out_v)
        self.matrix = self.compose(self.matrix, st_body.matrix, cr_mat)
        self.merge(self.vars, ex_vars, st_body.vars)
        self.merge(self.in_v, st_body.in_v)
        self.merge(self.out_v, st_body.out_v)

    def __if(self, ctx: JavaParser.StatementContext):
        self.corr_stmt(ctx.getChild(1), ctx.getChild(2))
        if ctx.getChildCount() > 4:  # else branch
            self.corr_stmt(ctx.getChild(1), ctx.getChild(4))

    def __while(self, ctx: JavaParser.StatementContext):
        self.corr_stmt(ctx.getChild(1), ctx.getChild(2))


def default_out(input_file: str) -> str:
    file_only = os.path.splitext(input_file)[0]
    file_name = '_'.join(file_only.split('/')[1:])
    return os.path.join("output", f"{file_name}.json")


def save_result(file_name: str, content: dict):
    dir_path, _ = os.path.split(file_name)
    if len(dir_path) > 0 and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_name, "w") as outfile:
        json.dump(content, outfile, indent=4)


if __name__ == '__main__':
    analyze(sys.argv[1], default_out(sys.argv[1]))
