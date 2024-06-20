from analysis import AbstractAnalyzer


def test_default_out_varying_path_depth():
    out = 'output'

    depth1 = 1
    input1 = "home/user/directory/package/filename.java"
    expect1 = "output/package_filename.json"

    depth2 = 3
    input2 = "~/library/Aliasing-ControlFlow-Insecure/program/src/Main.java"
    expect2 = "output/Aliasing-ControlFlow-Insecure_program_src_Main.json"

    assert AbstractAnalyzer.default_out(input1, out, depth1) == expect1
    assert AbstractAnalyzer.default_out(input2, out, depth2) == expect2
