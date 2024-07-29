from analysis import Result
from analysis.parser import JavaLexer, JavaParser, JavaParserVisitor
from analysis.analyzer.java import ExtVisitor
from antlr4 import CommonTokenStream, InputStream


def from_str(s):
    prog = "public class Program { static protected void main() { " + s + "}}"
    parser = JavaParser(CommonTokenStream(JavaLexer(InputStream(prog))))
    return parser, parser.compilationUnit()


def prog_builder(ex):
    p, t = from_str(ex)
    assert p.getNumberOfSyntaxErrors() == 0
    return (t.getChild(0).getChild(1).getChild(2)
            .getChild(1).getChild(2).getChild(0)
            .getChild(3).getChild(0).getChild(1))  # body


def p_errors(s):
    return from_str(s)[0].getNumberOfSyntaxErrors()


def RHS(s):  # node on right-hand-side of assignment
    return (prog_builder(s).getChild(0).getChild(1)
            .getChild(0).getChild(2).getChild(0))


def new(s):  # expression immediately after new
    return RHS(s).getChild(1)


def test_is_array_init():
    assert ExtVisitor.is_array_init(new("int[] a = new int[5];"))
    assert ExtVisitor.is_array_init(new("int[] a = new int[]{1, 2, 3, 4, 5};"))


def test_array_initializer():
    assert ExtVisitor.is_array_init(RHS("int[] a = {};"))
    assert ExtVisitor.is_array_init(RHS("int[] a = { 5 };"))
    assert ExtVisitor.is_array_init(RHS("int[] a = { 1, 2, 3 };"))
    assert ExtVisitor.is_array_init(RHS("int[] a = { obj(), obj() };"))


def test_is_array_init_ndim():
    assert ExtVisitor.is_array_init(new("int[] a = new int[5][5];"))
    assert ExtVisitor.is_array_init(new("int[] a = new int[2][];"))
    assert ExtVisitor.is_array_init(new("int[] a = new Object[2][][];"))


def test_not_array_init():
    assert ExtVisitor.is_array_init(RHS("int[] a = arr;")) is False
    assert ExtVisitor.is_array_init(RHS("int[] a = 5 + 5;")) is False


def test_nonsensical_init_fails_to_parse():
    # if these cannot parse we do not care about
    # how they are recognized internally
    assert p_errors("int[] a = arr[];") > 0
    assert p_errors("int[][] a = arr[][8];") > 0
    assert p_errors("int[] a = new int[3]{1, 2, 3};") > 0
    assert p_errors("int[][] a = arr[][8][];") > 0


def test_array_access():
    assert ExtVisitor.is_array_exp(RHS("int x = A[10];"))
    assert ExtVisitor.is_array_exp(RHS("int x = A[i][j];"))
