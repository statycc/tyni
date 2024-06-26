from analysis import BaseVisitor, AbstractAnalyzer as Abs
from pytest import raises


def test_default_out_varying_path_depth():
    in_ = "~/library/Aliasing-ControlFlow-Insecure" \
          "/program/src/Main.java"
    assert (Abs.default_out(in_, 'output', 0)
            == "output/Main.json")
    assert (Abs.default_out(in_, 'output', 1)
            == "output/src_Main.json")
    assert (Abs.default_out(in_, 'output', 3)
            == "output/Aliasing-ControlFlow-Insecure"
               "_program_src_Main.json")


def test_u_sub_positive():
    assert BaseVisitor.u_sub(10) == "₁₀"
    assert BaseVisitor.u_sub(589) == "₅₈₉"
    assert BaseVisitor.u_sub(0) == "₀"


def test_u_sub_negative():
    with raises(Exception):
        BaseVisitor.u_sub(-10)


def test_gen_rename():
    known = ['a', 'a₁', 'a₃', 'a₄']
    fst = BaseVisitor.uniq_name('a', known)
    snd = BaseVisitor.uniq_name('a', known + [fst])
    thr = BaseVisitor.uniq_name('a', known + [fst, snd])
    assert fst == 'a₂'
    assert snd == 'a₅'
    assert thr == 'a₆'
