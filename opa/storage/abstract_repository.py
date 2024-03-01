from typing import List, Optional
from opa.storage.abstract_model import HbaseEntity
from opa.utils import retry_connection_on_brokenpipe, retry_connection_on_ttransportexception
import pandas as pd
import happybase as hb


class HbaseCrudRepository:
    """
    Class for generic CRUD operations on a Hbase repository for a specific type.
    """

    def __init__(self, table_name: str, schema: Dict[str,Dict], host="localhost", port=9090, pool_size=3):
        """
        Initialize Hbase client  and create table if not already exist
        :param schema:
        """
        self.host = host
        self.port = port
        self.table_name = table_name
        self.pool = hb.ConnectionPool(size=pool_size, host=self.host, port=self.port)
        self.__create_if_not_exist_table(schema)

    @retry_connection_on_ttransportexception
    def save(self, entity: HbaseEntity) -> HbaseEntity:
        """
        Saves a given entity. Use the returned instance for further operations as the save operation might have changed
        the entity instance complet
        :param entity: must not be null.
        :return: he saved entity; will never be null.
        """
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            table.put(entity.id(), entity.value())

        return entity

    @retry_connection_on_brokenpipe(5)
    def save_all(self, entities: List[HbaseEntity], **options) -> List[HbaseEntity]:
        """
        Saves all given entities.
        :param entities: must not be null nor must it contain null.
        :return: the saved entities; will never be null. The returned List will have the same size as the List passed as
         an argument.
        """
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            with table.batch(**options) as b:
                for entity in entities:
                    b.put(entity.id(), entity.value())

        return entities

    def find_by_id(self, id: str) -> Optional[HbaseEntity]:
        """
        Retrieves an entity by its id.
        :param id: must not be null.
        :return: the entity with the given id or Optional#empty() if none found.
        """
        entity = None

        with self.pool.connection() as con:
            table = con.table(self.table_name)
            result = table.row(row=id)

        if result:
            entity = HbaseEntity()
            entity.load(result)

        return entity

    def find_all_prefix_id(self, prefix_id: str) -> List[HbaseEntity]:
        """
        Returns all instances of the type HbaseEntity
        with the ids that match with given prefix ID.
        :return: all entities
        """
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            candlesticks = [data for key, data in table.scan(row_prefix=prefix_id)]


    @abstractmethod
    def find_all_by_id(self, ids: List[str]) -> List[HbaseEntity]:
        """
        Returns all instances of the type HbaseEntity with the given IDs.
        If some or all ids are not found, no entities are returned for these IDs.
        Note that the order of elements in the result is not guaranteed.
        :param ids: must not be null nor contain any null values.
        :return: guaranteed to be not null. The size can be equal or less than the number of given ids.
        """
        pass

    @abstractmethod
    def exists_by_id(self, id: str) -> bool:
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
    def delete(self, data: HbaseEntity) -> None:
        """
        Deletes a given entity.
        :param data: must not be null.
        :return:
        """
        pass

    @abstractmethod
    def delete_by_id(self, id: str) -> None:
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

    @abstractmethod
    def delete_all_by_entities(self, entities: List[HbaseEntity]) -> None:
        """
        Deletes the given entities.
        :param entities: must not be null. Must not contain null elements.
        :return:
        """
        pass

    @abstractmethod
    def delete_all_by_id(self, ids: List[str]) -> None:
        """
        Deletes all instances of the type HbaseEntity with the given IDs.
        Entities that aren't found in the persistence store are silently ignored.
        :param ids: must not be null. Must not contain null elements.
        :return:
        """
        pass
