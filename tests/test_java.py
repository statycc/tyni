from analysis import JavaAnalyzer


def helper(prog, cls_name, method):
    res = JavaAnalyzer(prog).parse().run()[cls_name][method]
    return sorted(res['variables']), res['flows']


def test_ifc_prog1():
    vrs, flows = helper(
        'programs/IFCprog1/Program.java',
        'Program', 'example')
    assert vrs == ['x', 'y', 'z']
    assert ('x', 'y') in flows
    assert ('y', 'x') in flows
    assert ('z', 'x') in flows
    assert ('z', 'y') in flows
    assert len(flows) == 4


def test_ifc_prog2a():
    vrs, flows = helper(
        'programs/IFCprog2a/Program.java',
        'Program', 'example')
    assert vrs == ['w', 'x', 'y', 'z']
    assert ('x', 'w') in flows
    assert ('y', 'x') in flows
    assert ('y', 'z') in flows
    assert len(flows) == 3


def test_ifc_prog2b():
    vrs, flows = helper(
        'programs/IFCprog2b/Program.java',
        'Program', 'example')
    assert vrs == ['w', 'x', 'y', 'z']
    assert ('w', 'z') in flows
    assert ('x', 'z') in flows
    assert ('y', 'z') in flows
    assert ('w', 'x') in flows
    assert ('x', 'w') in flows
    assert ('y', 'x') in flows
    assert len(flows) == 6


def test_ifc_prog3():
    vrs, flows = helper(
        'programs/IFCprog3/Program.java',
        'Program', 'example')
    assert vrs == ['i', 'j', 's1', 's2', 't']
    assert ('t', 'i') in flows
    assert ('j', 'i') in flows
    assert ('t', 's1') in flows
    assert ('i', 's1') in flows
    assert ('j', 's1') in flows
    assert ('t', 's2') in flows
    assert ('i', 's2') in flows
    assert ('j', 's2') in flows
    assert len(flows) == 8


def test_ifc_ex1():
    vrs, flows = helper(
        'programs/IFCex1/Program.java',
        'Program', 'example')
    assert vrs == ['h', 'y', 'z']
    assert ('h', 'y') in flows
    assert ('y', 'z') in flows
    assert ('z', 'y') in flows
    assert len(flows) == 3


def test_ifc_ex2():
    vrs, flows = helper(
        'programs/IFCex1/Program.java',
        'Program', 'example')
    assert vrs == ['x', 'y', 'z']
    assert ('y', 'x') in flows
    assert ('z', 'x') in flows
    assert len(flows) == 2
