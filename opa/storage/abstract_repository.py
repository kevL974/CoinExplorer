from typing import TypeVar, List, Optional, Generic, AnyStr, Dict, Type
from abc import ABC, abstractmethod


class Entity(ABC):
    pass
class HbaseEntity(ABC,Entity):

    @abstractmethod
    def value(self) -> Dict:
        pass

    @abstractmethod
    def id(self) -> str:
        pass


T = TypeVar('T', covariant=True,bound='Entity')
ID = TypeVar('ID', covariant=True, bound=AnyStr)


class CrudRepository(ABC, Generic[T, ID]):
    """
    Interface for generic CRUD operations on a repository for a specific type.
    """

    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Saves a given entity. Use the returned instance for further operations as the save operation might have changed
        the entity instance complet
        :param entity: must not be null.
        :return: he saved entity; will never be null.
        """
        pass

    @abstractmethod
    def save_all(self, entities: List[T]):
        """
        Saves all given entities.
        :param entities: must not be null nor must it contain null.
        :return: the saved entities; will never be null. The returned List will have the same size as the List passed as
         an argument.
        """
        pass

    @abstractmethod
    def find_by_id(self, id: ID) -> Optional[T]:
        """
        Retrieves an entity by its id.
        :param id: must not be null.
        :return: the entity with the given id or Optional#empty() if none found.
        """
        pass

    @abstractmethod
    def find_all(self) -> List[T]:
        """
        Returns all instances of the type.
        :return: all entities
        """
        pass

    @abstractmethod
    def find_all_by_id(self, ids: List[ID]) -> List[T]:
        """
        Returns all instances of the type T with the given IDs.
        If some or all ids are not found, no entities are returned for these IDs.
        Note that the order of elements in the result is not guaranteed.
        :param ids: must not be null nor contain any null values.
        :return: guaranteed to be not null. The size can be equal or less than the number of given ids.
        """
        pass

    @abstractmethod
    def exists_by_id(self, id: ID) -> bool:
        """
        Returns whether an entity with the given id exists.
        :param id: must not be null.
        :return: true if an entity with the given id exists, false otherwise.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Returns the number of entities available.
        :param id:
        :return: the number of entities.
        """
        pass

    @abstractmethod
    def delete(self, data: T) -> None:
        """
        Deletes a given entity.
        :param data: must not be null.
        :return:
        """
        pass

    @abstractmethod
    def delete_by_id(self, id: ID) -> None:
        """
        Deletes the entity with the given id.
        If the entity is not found in the persistence store it is silently ignored.
        :param id: must not be null.
        :return:
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """
        Deletes all entities managed by the repository.
        :return:
        """
        pass

    def delete_all_by_entities(self, entities: List[T]) -> None:
        """
        Deletes the given entities.
        :param entities: must not be null. Must not contain null elements.
        :return:
        """
        pass

    @abstractmethod
    def delete_all_by_id(self, ids: List[ID]) -> None:
        """
        Deletes all instances of the type T with the given IDs.
        Entities that aren't found in the persistence store are silently ignored.
        :param ids: must not be null. Must not contain null elements.
        :return:
        """
        pass


class HbaseRepository(ABC, CrudRepository[HbaseEntity, str]):
    pass
