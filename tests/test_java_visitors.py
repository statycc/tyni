from analysis import Result
from analysis.parser import JavaLexer, JavaParser, JavaParserVisitor
from analysis.analyzer.java import ExtVisitor
from antlr4 import CommonTokenStream, InputStream


def from_str(s):
    return JavaParser(CommonTokenStream(
        JavaLexer(InputStream(s)))).compilationUnit()


def test_array_exp():
    assert not ExtVisitor.is_array_exp(from_str("arr"))
    assert ExtVisitor.is_array_exp(from_str("arr[]"))
    assert ExtVisitor.is_array_exp(from_str("arr[5]"))
    assert ExtVisitor.is_array_exp(from_str("arr[][]"))
    assert ExtVisitor.is_array_exp(from_str("arr[8][]"))
    assert ExtVisitor.is_array_exp(from_str("arr[2][11]"))
    assert not ExtVisitor.is_array_exp(from_str("arr[][8]"))
    assert ExtVisitor.is_array_exp(from_str("arr[][][]"))
    assert ExtVisitor.is_array_exp(from_str("arr[2][][]"))
    assert not ExtVisitor.is_array_exp(from_str("arr[][5][]"))


def test_array_init():
    def prog_builder(ex):
        return (from_str(
            "public class Program { "
            "static protected void main() { "
            f"int[] arr = new int[]{ex};" + "; }}")
                .getChild(0).getChild(1).getChild(2)
                .getChild(1).getChild(2).getChild(0)
                .getChild(3).getChild(0).getChild(1)
                .getChild(0).getChild(1).getChild(0)
                .getChild(2).getChild(0).getChild(1)
                .getChild(1).getChild(2))  # { ... }

    assert ExtVisitor.is_array_init(prog_builder("{ }"))
    assert ExtVisitor.is_array_init(prog_builder("{ 5 }"))
    assert ExtVisitor.is_array_init(prog_builder("{1, 2, 3}"))
    assert ExtVisitor.is_array_init(prog_builder("{obj(), obj()}"))
