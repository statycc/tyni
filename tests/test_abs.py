from analysis import AbstractAnalyzer as Abs


def test_default_out_varying_path_depth():
    in_ = "~/library/Aliasing-ControlFlow-Insecure" \
          "/program/src/Main.java"
    assert Abs.default_out(in_, 'output', 0) == "output/Main.json"
    assert Abs.default_out(in_, 'output', 1) == "output/src_Main.json"
    assert Abs.default_out(in_, 'output', 3) == \
           "output/Aliasing-ControlFlow-Insecure" \
           "_program_src_Main.json"
