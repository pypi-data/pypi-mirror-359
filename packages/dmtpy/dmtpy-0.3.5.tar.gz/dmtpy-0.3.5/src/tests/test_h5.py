from pathlib import Path

from numpy import asarray

from dmt.h5.h5_reader import H5Reader
from dmt.h5.h5_writer import H5Writer

from tests.some_entity import SomeEntity
from tests.some_enum import SomeEnum


def test_write_h5(tmpdir):
    """Test that entites are written and read back via h5"""
    entity = SomeEntity()
    entity.myint = 2
    entity.myEnum = SomeEnum.OPTION2
    entity.myArray = asarray([1.0, 2.0])

    # Create names such that they are in reverse alphabetical order
    child1 = SomeEntity()
    child1.name = "b"
    child1.myint = 3

    child2 = SomeEntity()
    child2.name = "a"
    child2.myint = 4
    child2.myArray = asarray([3.0, 4.0])
    child2.ref = child1

    entity.children = [child1, child2]

    child3 = SomeEntity()
    child3.myint = 4
    child3.mystrings = asarray(["a","b"])
    entity.child = child3

    file = Path(tmpdir) / "test.h5"
    writer = H5Writer()
    writer.write([entity], file)

    assert file.exists()

    reader = H5Reader()
    entities = reader.read(file)
    assert len(entities) == 1

    entity2 = entities[0]

    assert entity2.myint == entity.myint
    assert (entity2.myArray == entity.myArray).all()
    assert entity2.myEnum == SomeEnum.OPTION2
    assert len(entity2.children) == 2
    child1_2=entity2.children[0]
    child2_2=entity2.children[1]
    # check order
    assert child1_2.name == "b"
    assert child2_2.name == "a"
    # Check cross reference
    assert child2_2.ref == child1_2
