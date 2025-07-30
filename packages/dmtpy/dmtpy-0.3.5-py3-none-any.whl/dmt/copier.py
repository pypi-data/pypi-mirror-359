from typing import Sequence
from dmt.blueprint import Blueprint
from dmt.blueprint_attribute import BlueprintAttribute
from .entity import Entity

class Copier:

    def __init__(self,keep_uncontained_references=True):
        """Create a copier
        keep_uncontained_references: If True, uncontained references will be copied as well, otherwise they will be removed
        """
        self.__copies = {}
        self.keep_uncontained_references = keep_uncontained_references

    def copy(self, entity: Entity) -> Entity:
        """Copy an entity"""
        self.__copies = {}
        copy = self.__copy_entity(entity)
        self.__copy_containment(entity,copy)
        self.__copy_references()
        return copy
    
    def copy_all(self, entities: Sequence[Entity]) -> Sequence[Entity]:
        """Copy entities"""
        self.__copies = {}
        copies = [self.__copy_entity(entity) for entity in entities]
        self.__copy_references()
        return copies
            

    def __copy_entity(self, entity: Entity) -> Entity:
        """Copy an entity"""
        cls = type(entity)
        copy = cls()
        self.__copies[entity] = copy
        self.__copy_containment(entity,copy)
        return copy
    
    def __copy_containment(self, entity: Entity, copy: Entity):
        bp: Blueprint=entity.blueprint
        for attribute in bp.attributes:
            if entity.is_set(attribute):
                value=entity.get(attribute)
                if isinstance(attribute,BlueprintAttribute):
                    bpa: BlueprintAttribute=attribute
                    if bpa.contained:
                        if bpa.has_dimensions():
                            children: Sequence[Entity] = value
                            copies = [copy for copy in [self.__copy_entity(child) for child in children]]
                            copy.set(attribute,copies)
                        else:
                            child_copy = self.__copy_entity(value)
                            copy.set(attribute,child_copy)
                        
                else:
                    copy.set(attribute,value)

    def __copy_references(self):
        for entity, copy in self.__copies.items():
            bp: Blueprint=entity.blueprint
            for bpa in bp.blueprint_attributes():
                if not bpa.contained:
                    value=entity.get(bpa)
                    if value:
                        if bpa.has_dimensions():
                            refs: Sequence[Entity] = value
                            copies = []
                            for ref in refs:
                                child_copy = self.__copies.get(ref)
                                if child_copy:
                                    copies.append(child_copy)
                                elif self.keep_uncontained_references:
                                    copies.append(ref)
                            copy.set(bpa,copies)
                        else:
                            ref = value
                            child_copy = self.__copies.get(ref)
                            if child_copy:
                                copy.set(bpa,child_copy)
                            elif self.keep_uncontained_references:
                                copy.set(bpa,ref)
                
