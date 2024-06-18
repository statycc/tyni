#!/usr/bin/env python3

import sys
from antlr4 import *
from src import JavaLexer, JavaParser, JavaParserVisitor


def main(argv):
    input_stream = FileStream(argv[1])
    lexer = JavaLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = JavaParser(stream)
    if parser.getNumberOfSyntaxErrors() > 0:
        print("syntax errors")
    else:
        tree = parser.compilationUnit()
        VisitorInterp().visit(tree)


class VisitorInterp(JavaParserVisitor):

    def visitMethodDeclaration(
            self, ctx: JavaParser.MethodDeclarationContext):
        ret_type = ctx.typeTypeOrVoid().getText()
        name = ctx.identifier().getText()
        body = ctx.methodBody()
        return print(name, ':', body.getText(), '\n')


if __name__ == '__main__':
    main(sys.argv)
