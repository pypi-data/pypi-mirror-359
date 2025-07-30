""" A basic Entity Istance"""

from __future__ import annotations
from enum import Enum

from typing import Iterator, Sequence, TypeVar,Dict

from dmt.blueprint import Blueprint
from dmt.dimension import Dimension
from dmt.attribute import Attribute


E = TypeVar("E")

class Entity():
    """ A basic Entity Istance"""

    def __init__(self, description="", **kwargs):
        self.description = description
        for key, value in kwargs.items():
            if not isinstance(value, Dict):
                setattr(self, key, value)

    @property
    def description(self) -> str:
        """Get description"""
        return self.__description

    @description.setter
    def description(self, value: str):
        """Set description"""
        self.__description = str(value)

    @property
    def blueprint(self) -> Blueprint:
        """Return blueprint that this entity represents"""
        raise Exception("Should have been overridden")

    def get_dimension(self, dim: Dimension) -> int:
        """Get the dimension"""
        return getattr(self,dim.name,0)

    def is_set(self, prop: Attribute) -> bool:
        """Is the attribute set?"""
        value=getattr(self,prop.name,None)
        if value is None:
            return False
        if prop.is_string():
            if isinstance(value,Enum):
                return True
            return len(value) > 0
        if prop.has_dimensions():
            return len(value)>0
        return True
    
    def set(self, prop: Attribute, value: any):
        """Set the attribute"""
        setattr(self,prop.name,value)
    
    def get(self, prop: Attribute) -> any:
        """Get the attribute"""
        return getattr(self,prop.name,None)

    def content(self) -> Iterator[Entity]:
        """Get direct children contained in this entity"""
        for p in self.blueprint.blueprint_attributes():
            if p.contained and self.is_set(p):
                value = getattr(self, p.name, None)
                if p.has_dimensions():
                    children: Sequence[Entity] = value
                    for child in children:
                        yield child
                else:
                    child: Entity = value
                    yield child

    def all_content(self) -> Iterator[Entity]:
        """Get all children contained in this entity"""
        for p in self.blueprint.blueprint_attributes():
            if p.contained and self.is_set(p):
                value = getattr(self, p.name, None)
                if p.has_dimensions():
                    children: Sequence[Entity] = value
                    for child in children:
                        yield child
                        yield from child.all_content()
                else:
                    child: Entity = value
                    yield child
                    yield from child.all_content()

    def copy(self: E,keep_uncontained_references=True) -> E:
        """"Copy the entity"""
        from .copier import Copier
        return Copier(keep_uncontained_references).copy(self)
