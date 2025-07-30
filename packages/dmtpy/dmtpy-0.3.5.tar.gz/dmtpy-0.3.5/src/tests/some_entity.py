from dmt.blueprint import Blueprint
from dmt.attribute import Attribute
from dmt.blueprint_attribute import BlueprintAttribute
from dmt.enum_attribute import EnumAttribute
from dmt.entity import Entity
from dmt.dimension import Dimension
from tests.some_enum import SomeEnum
class SomeEntityBlueprint(Blueprint):

    """Blueprint used for testing"""

    def __init__(self):

        super().__init__(name="SomeEntity", package_path="tests")
        self.add_attribute(Attribute("name", "string", "", optional=False))
        self.add_attribute(Attribute("myint", "integer", "", optional=False, default=1))
        self.add_attribute(Attribute("mybool", "boolean", "", optional=True, default=True))
        self.add_attribute(Attribute("myArray", "number", "",Dimension("size")))
        self.add_attribute(BlueprintAttribute("children", self.get_path(), "",True,Dimension("size")))
        self.add_attribute(Attribute("mystrings", "string", "", Dimension("size")))
        self.add_attribute(BlueprintAttribute("child", self.get_path(), "",True))
        self.add_attribute(EnumAttribute("myEnum","tests/SomeEnum",""))
        self.add_attribute(BlueprintAttribute("ref", self.get_path(), "",False))
        self.add_attribute(BlueprintAttribute("refs", self.get_path(), "",False, Dimension("size")))


class SomeEntity(Entity):

    """An entity used for testing"""

    def __init__(self):
        super().__init__()
        self.__blueprint = SomeEntityBlueprint()
        self.name = None
        self.myint = 1
        self.mybool = True
        self.myArray = []
        self.children = []
        self.mystrings = []
        self.child = None
        self.myEnum = SomeEnum.OPTION1
        self.ref = None
        self.refs = []

    @property
    def blueprint(self) -> Blueprint:
        """Return blueprint that this entity represents"""
        return self.__blueprint


