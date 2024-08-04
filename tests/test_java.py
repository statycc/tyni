from analysis import Result
from analysis.analyzer import JavaAnalyzer


def helper(prog, cls_name, method):
    res = Result(f'programs/{prog}/Program.java')
    JavaAnalyzer(res).parse().analyze()
    mth = res.analysis_result[cls_name][method]
    return sorted(mth.ids), mth.flows, mth.skips


def test_ifc_prog1():
    vrs, flows, skips = helper('ifcprog1', 'Program', 'example')
    assert vrs == ['x', 'y', 'z']
    assert ('x', 'y') in flows
    assert ('y', 'x') in flows
    assert ('z', 'x') in flows
    assert ('z', 'y') in flows
    assert len(flows) == 4
    assert all(x.startswith('System.out.println') for x in skips)


def test_ifc_prog2a():
    vrs, flows, skips = helper('ifcprog2a', 'Program', 'example')
    assert vrs == ['w', 'x', 'y', 'z']
    assert ('x', 'w') in flows
    assert ('y', 'x') in flows
    assert ('y', 'z') in flows
    assert len(flows) == 3
    assert all(x.startswith('System.out.println') for x in skips)


def test_ifc_prog2b():
    vrs, flows, skips = helper('ifcprog2b', 'Program', 'example')
    assert vrs == ['w', 'x', 'y', 'z']
    assert ('w', 'z') in flows
    assert ('x', 'z') in flows
    assert ('y', 'z') in flows
    assert ('w', 'x') in flows
    assert ('x', 'w') in flows
    assert ('y', 'x') in flows
    assert len(flows) == 6
    assert all(x.startswith('System.out.println') for x in skips)


def test_ifc_prog3():
    vrs, flows, skips = helper('ifcprog3', 'Program', 'example')
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
    assert not skips


def test_ifc_ex1():
    vrs, flows, skips = helper('ifcex1', 'Program', 'example')
    assert vrs == ['h', 'y', 'z']
    assert ('h', 'y') in flows
    assert ('y', 'z') in flows
    assert ('z', 'y') in flows
    assert len(flows) == 3
    assert all(x.startswith('System.out.println') for x in skips)


def test_ifc_ex2():
    vrs, flows, skips = helper('ifcex2', 'Program', 'example')
    assert vrs == ['x', 'y', 'z']
    assert ('y', 'x') in flows
    assert ('z', 'x') in flows
    assert len(flows) == 2
    assert all(x.startswith('System.out.println') for x in skips)


def test_sql_injection():
    vrs, flows, skips = helper('sqlinject', 'Program', 'example')
    assert vrs == ['query', 'request', 'sb1', 'sb2', 'user']
    assert ('request', 'user') in flows
    assert ('user', 'sb1') in flows
    assert ('sb2', 'query') in flows
    assert len(flows) == 3
    assert skips == ['System.out.println(query)']


def test_mvt_kernel():
    vrs, flows, skips = helper('mvt', 'Program', 'mvt')
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
    assert not skips


def test_local_scoping():
    vrs, flows, skips = helper('localscope', 'Program', 'example')
    assert (set(vrs) == set('a,b,c,x,y,z,i,i₂,i₃,j,j₂,j₃'.split(',')))
    assert ('a', 'i') in flows
    assert ('a', 'j') in flows
    assert ('a', 'y') in flows
    assert ('b', 'i₂') in flows
    assert ('b', 'j₂') in flows
    assert ('b', 'x') in flows
    assert ('c', 'j₃') in flows
    assert ('i', 'j') in flows
    assert ('i', 'y') in flows
    assert ('i₂', 'j₂') in flows
    assert ('i₂', 'x') in flows
    assert ('i₃', 'y') in flows
    assert ('j', 'y') in flows
    assert ('j₂', 'x') in flows
    assert ('j₃', 'i₃') in flows
    assert ('j₃', 'y') in flows
    assert ('x', 'z') in flows
    assert ('y', 'z') in flows
    assert len(flows) == 18
    assert not skips


def test_object_creation():
    vrs, flows, skips = helper('objflow', 'Program', 'init')
    assert (set(vrs) == set(
        'MyClass₀,MyClass₁,MyClass₂,a,b,c,x,y'.split(',')))
    assert ('x', 'MyClass₀') in flows
    assert ('MyClass₀', 'a') in flows
    assert ('y', 'MyClass₁') in flows
    assert ('MyClass₁', 'b') in flows
    assert ('MyClass₂', 'c') in flows
    assert len(flows) == 5
    assert not skips
