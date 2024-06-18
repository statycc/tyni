#!/usr/bin/env python3

import sys
import json
import os
from antlr4 import *
from src import JavaLexer, JavaParser, JavaParserVisitor


def analyze(input_file, out_file):
    input_stream = FileStream(input_file)
    lexer = JavaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JavaParser(stream)
    if parser.getNumberOfSyntaxErrors() > 0:
        print("syntax errors")
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
        print('(!) method call:', ctx.getText())

    def visitStatement(self, ctx: JavaParser.StatementContext):
        """Statement handlers; see grammars/JavaParser.g4 L#508."""
        if ctx.blockLabel:
            print('block:', ctx.getText())
        elif ctx.ASSERT():
            print('assert:', ctx.getText())
        elif ctx.IF():
            return self.__if(ctx)
        elif ctx.FOR():
            print('for loop:', ctx.getText())
        elif ctx.WHILE():
            return self.__while(ctx)
        elif ctx.DO():
            print('do while loop:', ctx.getText())
        elif ctx.TRY():
            print('try block:', ctx.getText())
        elif ctx.SWITCH():
            print('switch:', ctx.getText())
        elif ctx.SYNCHRONIZED():
            print('sync:', ctx.getText())
        elif ctx.RETURN():
            print('return:', ctx.getText())
        elif ctx.THROW():
            print('throw:', ctx.getText())
        elif ctx.BREAK():
            print('break:', ctx.getText())
        elif ctx.CONTINUE():
            print('cont:', ctx.getText())
        elif ctx.YIELD():
            print('yield:', ctx.getText())
        elif ctx.SEMI():
            return self.__stmt_exp(ctx)
        elif ctx.statementExpression:
            return self.__stmt_exp(ctx)
        elif ctx.switchExpression():
            print('switch exp:', ctx.getText())
        elif ctx.identifierLabel:
            print('id label:', ctx.getText())
        else:
            print('(!) other:', ctx.getText())
        super().visitStatement(ctx)

    def __stmt_exp(self, ctx: JavaParser.StatementContext):
        print('stmt exp --', ctx.getText())
        super().visitStatement(ctx)

    def __if(self, ctx: JavaParser.StatementContext):
        exp, tb = ctx.getChild(1), ctx.getChild(2)
        exv, fbv = self.occurs(exp), RecVisitor()
        tbv = RecVisitor().visit(tb)
        if ctx.getChildCount() > 4:
            fb = ctx.getChild(4)
            fbv.visit(fb)
        self.merge(self.vars, exv, tbv.vars, fbv.vars)

    def __while(self, ctx: JavaParser.StatementContext):
        exp, body = ctx.getChild(1), ctx.getChild(2)
        ex_vars = self.occurs(exp)
        RecVisitor().visit(body)
        self.merge(self.vars, ex_vars)

    def visitExpression(self, ctx: JavaParser.ExpressionContext):
        super().visitExpression(ctx)
        print("exp", ctx.getText())


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
