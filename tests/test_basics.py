import json
import os

from pytest import raises

from analysis import BaseVisitor
from analysis import Result


def test_default_out_varying_path_depth():
    in_ = "~/lib/Aliasing-Insecure/prog/src/Main.java"
    def_o = lambda d: Result.default_out(in_, 'output', d)

    assert def_o(0) == "output/Main.json"
    assert def_o(1) == "output/src_Main.json"
    assert def_o(3) == "output/Aliasing-Insecure_prog_src_Main.json"


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


def test_save(mocker):
    # mock all built-ins
    mocker.patch('os.path.exists', return_value=False)
    mocker.patch('os.makedirs')
    mocker.patch('builtins.open')
    mocker.patch('json.dump')
    Result('my.c', 'out/my_dir/my.json').save()
    os.makedirs.assert_called_once_with('out/my_dir')
    json.dump.assert_called_once()
