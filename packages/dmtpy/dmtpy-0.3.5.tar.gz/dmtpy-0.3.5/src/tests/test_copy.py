"""
Tests for the copy functionality of the copier.
If keep_uncontained_references is true, references to entities that are not contained in the entity will be kept. If false, they will be removed.
Default is true.
"""
from dmt.copier import Copier
from tests.some_entity import SomeEntity
from tests.some_enum import SomeEnum

def test_simple_copy():
    e1 = __create_entity()
    e2 = e1.copy()
    __assert_equal(e1, e2)

def __create_entity(name="test"):
    entity = SomeEntity()
    entity.name = name
    entity.myint = 2
    entity.mybool = False
    entity.myArray = [1, 2, 3]
    entity.myEnum = SomeEnum.OPTION2
    return entity

def __assert_equal(e1: SomeEntity, e2: SomeEntity):
    assert e2.name == e1.name
    assert e2.myint == e1.myint
    assert e2.mybool == e1.mybool
    assert e2.myArray == e1.myArray
    assert e2.myEnum == e1.myEnum

def test_single_containment():
    e1 = __create_entity()
    e2 = __create_entity()
    e2.name = "test2"
    e1.child = e2

    e3 = e1.copy()
    __assert_equal(e2, e3.child)

def test_multi_containment():
    e1 = __create_entity("test1")
    e2 = __create_entity("test2")
    e3 = __create_entity("test3")
    e1.children = [e2,e3]

    e4 = e1.copy()
    __assert_equal(e2, e4.children[0])
    __assert_equal(e3, e4.children[1])


def test_single_contained_reference():
    e1 = __create_entity("e1")
    e2 = __create_entity("ref")
    # First we contain it
    e1.child = e2
    e1.ref = e2

    e3 = e1.copy()
    e4 = e3.child
    assert e3.ref is e4

def test_multi_contained_references():
    e1 = __create_entity("e1")
    e2 = __create_entity("ref1")
    e3 = __create_entity("ref2")
    # First we contain them
    
    e1.children = [e2,e3]
    
    e2.refs = [e1,e3]
    e3.refs = [e2,e3]

    e4 = e1.copy()
    e5 = e4.children[0]
    e6 = e4.children[1]

    assert e5.refs[0] is e4
    assert e5.refs[1] is e6
    assert e6.refs[0] is e5
    assert e6.refs[1] is e6


def test_single_uncontained_reference():
    e1 = __create_entity("e1")
    e2 = __create_entity("ref")
    # We just reference it without containing it
    e1.ref = e2

    e3 = e1.copy(False)
    # The reference should be gone, since it is not contained
    assert e3.ref is None

def test_uncontained_reference_copy():
    e1 = __create_entity("e1")
    e2 = __create_entity("ref")
    # We just reference it without containing it
    e1.ref = e2
    e2.ref = e1

    copier = Copier()
    e3,e4 = copier.copy_all([e1,e2])
    assert e3.ref is e4
    assert e4.ref is e3

def test_uncontained_reference_copy_keep_uncontained():
    e1 = __create_entity("e1")
    e2 = __create_entity("ref")
    # We just reference it without containing it
    e1.ref = e2
    e2.ref = e1

    copier = Copier(keep_uncontained_references=True)
    e3, = copier.copy_all([e1])
    assert e3.ref is e2
    assert e2.ref is e1
    

def test_multiple_uncontained_reference():
    e1 = __create_entity("e1")
    e2 = __create_entity("ref1")
    e3 = __create_entity("ref2")
    
    e1.refs = [e2,e3]

    e4 = e1.copy(keep_uncontained_references=False)
    # The references should be gone, since they are not contained
    assert e4.refs == []

    # Try once more with a copier
    copier = Copier(keep_uncontained_references=False)
    # First we only include one of the references
    e4,e5 = copier.copy_all([e1,e2])
    assert e4.refs == [e5]

    # Then all of them
    e4,e5,e6 = copier.copy_all([e1,e2,e3])
    assert e4.refs == [e5,e6]


