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
        tree = parser.packageDeclaration()
        vinterp = VisitorInterp()
        vinterp.visit(tree)


class VisitorInterp(JavaParserVisitor):
    def visitClassDeclaration(
            self, ctx: JavaParser.ClassDeclarationContext):
        return print(ctx.getText())

    # def visitExpr(self, ctx: JavaParser.ExprContext):
    #     if ctx.getChildCount() == 3:
    #         if ctx.getChild(0).getText() == "(":
    #             return self.visit(ctx.getChild(1))
    #         op = ctx.getChild(1).getText()
    #         v1 = self.visit(ctx.getChild(0))
    #         v2 = self.visit(ctx.getChild(2))
    #         if op == "+":
    #             return v1 + v2
    #         if op == "-":
    #             return v1 - v2
    #         if op == "*":
    #             return v1 * v2
    #         if op == "/":
    #             return v1 / v2
    #         return 0
    #     if ctx.getChildCount() == 2:
    #         opc = ctx.getChild(0).getText()
    #         if opc == "+":
    #             return self.visit(ctx.getChild(1))
    #         if opc == "-":
    #             return - self.visit(ctx.getChild(1))
    #         return 0
    #     if ctx.getChildCount() == 1:
    #         return self.visit(ctx.getChild(0))
    #     return 0

    def visitStatement(self, ctx: JavaParser.StatementContext):
        for i in range(0, ctx.getChildCount(), 2):
            print(self.visit(ctx.getChild(i)))
        return 0


if __name__ == '__main__':
    main(sys.argv)
