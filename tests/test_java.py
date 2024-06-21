from analysis import JavaAnalyzer


def helper(prog, cls_name, method):
    p = f'programs/{prog}/Program.java'
    res = JavaAnalyzer(p).parse().run()[cls_name][method]
    return sorted(res['variables']), res['flows']


def test_ifc_prog1():
    vrs, flows = helper('IFCprog1', 'Program', 'example')
    assert vrs == ['x', 'y', 'z']
    assert ('x', 'y') in flows
    assert ('y', 'x') in flows
    assert ('z', 'x') in flows
    assert ('z', 'y') in flows
    assert len(flows) == 4


def test_ifc_prog2a():
    vrs, flows = helper('IFCprog2a', 'Program', 'example')
    assert vrs == ['w', 'x', 'y', 'z']
    assert ('x', 'w') in flows
    assert ('y', 'x') in flows
    assert ('y', 'z') in flows
    assert len(flows) == 3


def test_ifc_prog2b():
    vrs, flows = helper('IFCprog2b', 'Program', 'example')
    assert vrs == ['w', 'x', 'y', 'z']
    assert ('w', 'z') in flows
    assert ('x', 'z') in flows
    assert ('y', 'z') in flows
    assert ('w', 'x') in flows
    assert ('x', 'w') in flows
    assert ('y', 'x') in flows
    assert len(flows) == 6


def test_ifc_prog3():
    vrs, flows = helper('IFCprog3', 'Program', 'example')
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
    vrs, flows = helper('IFCex1', 'Program', 'example')
    assert vrs == ['h', 'y', 'z']
    assert ('h', 'y') in flows
    assert ('y', 'z') in flows
    assert ('z', 'y') in flows
    assert len(flows) == 3


def test_ifc_ex2():
    vrs, flows = helper('IFCex2', 'Program', 'example')
    assert vrs == ['x', 'y', 'z']
    assert ('y', 'x') in flows
    assert ('z', 'x') in flows
    assert len(flows) == 2


def test_sql_injection():
    vrs, flows = helper('SqlInjection', 'Program', 'example')
    assert vrs == ['query', 'request', 'sb1', 'sb2', 'user']
    assert ('request', 'user') in flows
    assert ('user', 'sb1') in flows
    assert ('sb2', 'query') in flows
    assert len(flows) == 3


def test_mvt_kernel():
    vrs, flows = helper('MvtKernel', 'Program', 'mvt')
    assert vrs == 'A,N,i,j,x1,x2,y1,y2'.split(',')
    assert ('i', 'j') in flows
    assert ('N', 'j') in flows
    assert ('A', 'x1') in flows
    assert ('A', 'x2') in flows
    assert ('i', 'x1') in flows
    assert ('i', 'x2') in flows
    assert ('j', 'x1') in flows
    assert ('j', 'x2') in flows
    assert ('N', 'x1') in flows
    assert ('N', 'x2') in flows
    assert ('y1', 'x1') in flows
    assert ('y2', 'x2') in flows
    assert len(flows) == 13
