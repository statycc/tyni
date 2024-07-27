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

