#!/usr/bin/env python3

import sys
import json
import os
from antlr4 import *
from src import JavaLexer, JavaParser, JavaParserVisitor


def main(input_file, out_file):
    input_stream = FileStream(input_file)
    lexer = JavaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JavaParser(stream)
    if parser.getNumberOfSyntaxErrors() > 0:
        print("syntax errors")
    else:
        tree = parser.compilationUnit()
        visitor = VisitorInterp()
        visitor.visit(tree)
        result = {'in': input_file, 'mtx': visitor.result}
        save_result(out_file, result)


class VisitorInterp(JavaParserVisitor):

    def __init__(self):
        self.result = {}

    def record(self, n, **kwargs):
        self.result[n] = {**kwargs}

    def visitMethodDeclaration(
            self, ctx: JavaParser.MethodDeclarationContext):
        ret_type = ctx.typeTypeOrVoid().getText()
        name = ctx.identifier().getText()
        body = ctx.methodBody()
        params = IdVisitor().visit(ctx.formalParameters())
        b_visit = RecMethodVisitor(params)
        b_visit.visit(body)
        self.record(
            name,
            # 0: visitBlockStatement
            # 1: method body
            body=body.getChild(0).getChild(1).getText(),
            ret_type=ret_type,
            variables=list(b_visit.vars),
            matrix=b_visit.matrix)


class IdVisitor(JavaParserVisitor):

    def __init__(self):
        self.vars = {}

    def visit(self, tree):
        super().visit(tree)
        return self.vars

    def visitIdentifier(self, ctx: JavaParser.IdentifierContext):
        super().visitIdentifier(ctx)
        name = ctx.getText()
        self.vars[name] = name


class RecMethodVisitor(JavaParserVisitor):

    def __init__(self, init_vars=None):
        self.vars = init_vars or {}
        self.matrix = {}

    def visitBlockStatement(
            self, ctx: JavaParser.BlockStatementContext):
        super().visitBlockStatement(ctx)
        print('-' * 40)

    def visitMethodCall(self, ctx: JavaParser.MethodCallContext):
        super().visitMethodCall(ctx)
        print('method call:', ctx.getText())

    def visitStatement(self, ctx: JavaParser.StatementContext):
        if ctx.IF():
            self.__if(ctx)
        else:
            print(ctx.getText())
            super().visitStatement(ctx)

    def __if(self, ctx: JavaParser.StatementContext):
        cond = ctx.getChild(1)
        occ = self.occurs(cond)
        true_branch = ctx.getChild(2).getText()
        else_branch = None if ctx.getChildCount() < 5 \
            else ctx.getChild(4).getText()
        print("if stmt:",
              cond.getText(), '->', list(occ),
              '\n', true_branch, '\n', else_branch)

    def occurs(self, exp: JavaParser.ExpressionContext):
        occ_vars = IdVisitor().visit(exp)
        self.vars.update(occ_vars)
        return occ_vars


def default_out(input_file: str) -> str:
    file_only = os.path.splitext(input_file)[0]
    file_name = '_'.join(file_only.split('/')[1:])
    # file_name = os.path.basename(file_only)
    return os.path.join("output", f"{file_name}.json")


def save_result(file_name: str, file_content: dict):
    dir_path, _ = os.path.split(file_name)
    if len(dir_path) > 0 and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    with open(file_name, "w") as outfile:
        json.dump(file_content, outfile, indent=4)


if __name__ == '__main__':
    main(sys.argv[1], default_out(sys.argv[1]))
