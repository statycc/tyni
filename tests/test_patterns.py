from antlr4 import CommonTokenStream, InputStream

from analysis.analyzer.java import ExtVisitor
from analysis.parser import JavaLexer, JavaParser

INIT = ExtVisitor.is_array_init
EXP = ExtVisitor.is_array_exp


def from_str(body_stmt):
    parser = JavaParser(CommonTokenStream(JavaLexer(InputStream(
        "public class Program {static protected void main(){ "
        + body_stmt + "}}"))))
    tree = parser.compilationUnit()
    n_errors = parser.getNumberOfSyntaxErrors()
    return n_errors, tree


def prog_builder(ex):
    n_err, t = from_str(ex)
    assert n_err == 0  # no syntax errors
    return (t.getChild(0).getChild(1).getChild(2)
            .getChild(1).getChild(2).getChild(0)
            .getChild(3).getChild(0).getChild(1))  # body


def rhs(s):  # right-hand-side of assignment (assume typed lhs)
    return (prog_builder(s).getChild(0).getChild(1)
            .getChild(0).getChild(2).getChild(0))


def lhs(s):  # left-hand-side of assignment
    return prog_builder(s).getChild(0).getChild(0).getChild(0)


def test_is_array_init():
    assert INIT(rhs("int a = new int[5];").getChild(1))
    assert INIT(rhs("int a = new int[]{1, 2, 3, 4, 5};").getChild(1))


def test_array_initializer():
    assert INIT(rhs("int[] a = {};"))
    assert INIT(rhs("int[] a = { 5 };"))
    assert INIT(rhs("int[] a = { 1, 2, 3 };"))
    assert INIT(rhs("int[] a = { obj(), obj() };"))


def test_is_array_init_ndim():
    assert INIT(rhs("int[] a = new int[5][5];").getChild(1))
    assert INIT(rhs("int[] a = new int[2][];").getChild(1))
    assert INIT(rhs("int[] a = new Object[2][][];").getChild(1))


def test_not_array_init():
    assert INIT(rhs("int[] a = arr;")) is False
    assert INIT(rhs("int[] a = 5 + 5;")) is False


def test_array_access():
    assert EXP(rhs("int x = A[10];"))
    assert EXP(rhs("int x = A[i][j];"))
    assert EXP(lhs("A[10] = 10;"))
    assert EXP(lhs("B[x][y] = call();"))


def test_nonsensical_init_fails_to_parse():
    # test that these cannot parse
    # we do not care about how they are recognized internally.
    assert from_str("int[] a = arr[];")[0] > 0
    assert from_str("int[] a = new int[3]{1, 2, 3};")[0] > 0
    assert from_str("int[][] a = arr[][8];")[0] > 0
    assert from_str("int[][][] a = arr[][8][];")[0] > 0
