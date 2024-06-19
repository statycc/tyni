import logging
import operator
import sys
from functools import reduce
from itertools import product

from antlr4 import FileStream, CommonTokenStream

from src import AbstractAnalyzer
from src.parser.JavaLexer import JavaLexer
from src.parser.JavaParser import JavaParser
from src.parser.JavaParserVisitor import JavaParserVisitor

logger = logging.getLogger(__name__)


class JavaAnalyzer(AbstractAnalyzer):

    @staticmethod
    def lang_match(f_name: str) -> bool:
        return f_name and f_name.endswith('.java')

    def parse(self, exit_on_error: bool = False):
        input_stream = FileStream(self.input_file)
        lexer = JavaLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = JavaParser(stream)
        if parser.getNumberOfSyntaxErrors() > 0:
            logger.error("syntax errors")
            not exit_on_error or sys.exit(1)
        else:
            logger.debug("parsed successfully")
            self.tree = parser.compilationUnit()
        return self

    def analyze(self):
        assert self.tree
        result = MethodVisitor().visit(self.tree).result
        self.save(result)


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
        name = ctx.identifier().getText()
        logger.debug(f'analyzing method: {name}')
        prog = RecVisitor().visit(ctx.methodBody())
        self.record(name,
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
            # in compound case, an out-var is also an in-variable,
            # but we don't care about that relationship.
            if op in ['=', '+=', '-=', '*=', '/=', '%=']:
                # TODO: refine, left-hand could be an array
                out_v = IdVisitor().visit(ctx.getChild(0)).vars
                in_v = IdVisitor().visit(ctx.getChild(2)).vars
                self.merge(self.vars, out_v, in_v)
                self.merge(self.out_v, out_v)
                flows = self.assign(in_v, out_v)
                self.matrix = self.compose(self.matrix, flows)

            elif op in ['&=', '|=', '^=', '>>=', '>>>=', '<<=', ]:
                logger.warning("TODO:", op)

        elif ctx.getChildCount() == 2:
            v1 = ctx.getChild(0).getText()
            v2 = ctx.getChild(1).getText()
            if v1 in ['++', '--'] or v2 in ['++', '--']:
                in_v = out_v = IdVisitor().visit(ctx).vars
                self.merge(self.vars, in_v)
                self.merge(self.out_v, out_v)
        else:
            super().visitExpression(ctx)

    def corr_stmt(self, exp, body):
        ex_vars = self.occurs(exp)
        st_body = RecVisitor().visit(body)
        cr_mat = self.correction(ex_vars, st_body.out_v)
        self.matrix = self.compose(self.matrix, st_body.matrix, cr_mat)
        self.merge(self.vars, ex_vars, st_body.vars)
        self.merge(self.out_v, st_body.out_v)

    def __if(self, ctx: JavaParser.StatementContext):
        self.corr_stmt(ctx.getChild(1), ctx.getChild(2))
        if ctx.getChildCount() > 4:  # else branch
            self.corr_stmt(ctx.getChild(1), ctx.getChild(4))

    def __while(self, ctx: JavaParser.StatementContext):
        self.corr_stmt(ctx.getChild(1), ctx.getChild(2))
