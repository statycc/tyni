#!/usr/bin/env python3

import sys
import json
import os
import logging
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

    def visitMethodDeclaration(
            self, ctx: JavaParser.MethodDeclarationContext):
        ret_type = ctx.typeTypeOrVoid().getText()
        name = ctx.identifier().getText()
        body = ctx.methodBody()
        b_visit = RecVisitor().visit(body)
        self.record(
            name,
            # 0: visitBlockStatement
            # 1: method body -- it is not necessary to keep this
            body=body.getChild(0).getChild(1).getText(),
            ret_type=ret_type,
            variables=list(b_visit.vars),
            matrix=b_visit.matrix)


class RecVisitor(ExtVisitor):
    """Recursively process method body"""

    def __init__(self, init_vars=None):
        self.vars = init_vars or {}
        self.matrix = {}

    @staticmethod
    def merge(target, *args):
        [target.update(m) for m in args]

    @staticmethod
    def occurs(exp: JavaParser.ExpressionContext):
        return IdVisitor().visit(exp).vars

    def in_vars(self):
        return list(self.matrix.keys())

    def out_vars(self):
        return list(self.matrix.values())

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
        super().visitMethodCall(ctx)
        logger.error(f'(!) method call: {ctx.getText()}')

    def visitStatement(self, ctx: JavaParser.StatementContext):
        """Statement handlers, grammars/JavaParser.g4#L508"""
        if ctx.blockLabel:
            logger.debug(f'block: {ctx.getText()}')
        elif ctx.ASSERT():
            logger.debug(f'assert: {ctx.getText()}')
        elif ctx.IF():
            return self.__if(ctx)
        elif ctx.FOR():
            logger.debug(f'for loop: {ctx.getText()}')
        elif ctx.WHILE():
            return self.__while(ctx)
        elif ctx.DO():
            logger.debug(f'do while loop: {ctx.getText()}')
        elif ctx.TRY():
            logger.debug(f'try block: {ctx.getText()}')
        elif ctx.SWITCH():
            logger.debug(f'switch: {ctx.getText()}')
        elif ctx.SYNCHRONIZED():
            logger.debug(f'sync: {ctx.getText()}')
        elif ctx.RETURN():
            logger.debug(f'return: {ctx.getText()}')
        elif ctx.THROW():
            logger.debug(f'throw: {ctx.getText()}')
        elif ctx.BREAK():
            logger.debug(f'break: {ctx.getText()}')
        elif ctx.CONTINUE():
            logger.debug(f'cont: {ctx.getText()}')
        elif ctx.YIELD():
            logger.debug(f'yield: {ctx.getText()}')
        elif ctx.SEMI():
            return self.__stmt_exp(ctx)
        elif ctx.statementExpression:
            return self.__stmt_exp(ctx)
        elif ctx.switchExpression():
            logger.debug(f'switch exp: {ctx.getText()}')
        elif ctx.identifierLabel:
            logger.debug(f'id label: {ctx.getText()}')
        else:
            logger.debug(f'(!) other: {ctx.getText()}')
        super().visitStatement(ctx)

    def visitExpression(self, ctx: JavaParser.ExpressionContext):
        """Expressions, grammars/JavaParser.g4#L599"""
        logger.debug(f'-- exp {ctx.getText()}')
        super().visitExpression(ctx)

    def __stmt_exp(self, ctx: JavaParser.StatementContext):
        for child in ctx.getChildren():
            logger.debug(f'stmt exp ch: {child.getText()}')
        super().visitStatement(ctx)

    def __if(self, ctx: JavaParser.StatementContext):
        ex_vars = self.occurs(ctx.getChild(1))
        branch_t = RecVisitor().visit(ctx.getChild(2))
        branch_f = RecVisitor()
        if ctx.getChildCount() > 4:
            branch_f.visit(ctx.getChild(4))
        self.merge(self.vars, ex_vars, branch_t.vars, branch_f.vars)

    def __while(self, ctx: JavaParser.StatementContext):
        ex_vars = self.occurs(ctx.getChild(1))
        loop_body = RecVisitor().visit(ctx.getChild(2))
        self.merge(self.vars, ex_vars, loop_body.vars)


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
