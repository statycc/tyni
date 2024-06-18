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

    def cap_method(self, r, n, b):
        self.result[n] = {'ret_type': r, 'body': b}

    def visitMethodDeclaration(
            self, ctx: JavaParser.MethodDeclarationContext):
        body = ctx.methodBody()
        name = ctx.identifier().getText()
        ret_t = ctx.typeTypeOrVoid().getText()
        self.cap_method(ret_t, name, body.getText())
        return print(name, ':', body.getText(), '\n')


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
