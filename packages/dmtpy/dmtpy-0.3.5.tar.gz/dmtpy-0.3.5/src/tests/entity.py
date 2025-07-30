
from dmt.blueprint import Blueprint
from dmt.entity import Entity


class PyTestEntity(Entity):
    """Enables dynamic entities"""

    def __init__(self, blueprint: Blueprint):
        super().__init__()
        self.__blueprint = blueprint

    @property
    def blueprint(self) -> Blueprint:
        """Return blueprint that this entity represents"""
        return self.__blueprint
