from typing import List, Dict, Optional
from opa.storage.model import HbaseEntity
from opa.utils import retry_connection_on_brokenpipe, retry_connection_on_ttransportexception
import happybase as hb


class HbaseCrudRepository:
    """
    Class for generic CRUD operations on a Hbase repository for a specific type.
    """

    def __init__(self, table_name: str, schema: Dict[str, Dict], host="localhost", port=9090, pool_size=3):
        """
        Initialize Hbase client  and create table if not already exist
        :param schema:
        """
        self.host = host
        self.port = port
        self.table_name = table_name
        self.pool = hb.ConnectionPool(size=pool_size, host=self.host, port=self.port)
        self.__create_if_not_exist_table(schema)

    @retry_connection_on_ttransportexception(5)
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

    @retry_connection_on_ttransportexception(5)
    def find_by_id(self, id: str) -> Optional[Dict]:
        """
        Retrieves an entity by its id.
        :param id: must not be null.
        :return: the entity with the given id or Optional#empty() if none found.
        """
        result = None
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            result = table.row(row=id)

        return result

    @retry_connection_on_brokenpipe(5)
    def find_all_prefix_id(self, prefix_id: str) -> List[Dict]:
        """
        Returns all instances of the type HbaseEntity
        with the ids that match with given prefix ID.
        :return: all entities
        """
        results = []
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            results.extend(table.scan(row_prefix=prefix_id))

        return results

    @retry_connection_on_brokenpipe(5)
    def find_all_by_id(self, ids: List[str]) -> List[Dict]:
        """
        Returns all instances of the type HbaseEntity with the given IDs.
        If some or all ids are not found, no entities are returned for these IDs.
        Note that the order of elements in the result is not guaranteed.
        :param ids: must not be null nor contain any null values.
        :return: guaranteed to be not null. The size can be equal or less than the number of given ids.
        """
        results = []
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            results.extend(table.rows(rows=ids))

        return results

    @retry_connection_on_brokenpipe(5)
    def find_all_between_ids(self, start_id: str, end_id: str) -> List[Dict]:
        """
        Returns all instances of the type HbaseEntity between two IDs.
        If some or all ids are not found, no entities are returned for these IDs.
        Note that the order of elements in the result is not guaranteed.
        :param start_id: ID where the scanner should start.
        :param end_id: ID where the scanner should stop.
        :return: guaranteed to be not null.
        """
        results = []
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            results.extend(table.scan(row_start=start_id, row_stop=end_id))

        return results

    @retry_connection_on_ttransportexception(5)
    def exists_by_id(self, id: str) -> bool:
        """
        Returns whether an entity with the given id exists.
        :param id: must not be null.
        :return: true if an entity with the given id exists, false otherwise.
        """
        return self.find_all_by_id(id) is not None

    @retry_connection_on_brokenpipe(5)
    def count(self, filter: str=None) -> int:
        """
        Returns the number of entities available.
        :param filter: a filter string (optional)
        :return: the number of entities.
        """
        count = 0
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            for _ in table.scan(filter=filter):
                count += 1

        return count

    @retry_connection_on_ttransportexception(5)
    def delete(self, entity: HbaseEntity) -> None:
        """
        Deletes a given entity.
        :param entity: must not be null.
        :return:
        """
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            table.delete(row=entity.id())

    @retry_connection_on_ttransportexception(5)
    def delete_by_id(self, id: str) -> None:
        """
        Deletes the entity with the given id.
        If the entity is not found in the persistence store it is silently ignored.
        :param id: must not be null.
        :return:
        """
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            table.delete(row=id)

    @retry_connection_on_brokenpipe(5)
    def delete_all(self) -> None:
        """
        Deletes all entities managed by the repository.
        :return:
        """
        with self.pool.connection() as con:
            if not con.is_table_enabled(self.table_name):
                con.disable_table(self.table_name)
            con.delete_table(self.table_name)

    @retry_connection_on_brokenpipe(5)
    def delete_all_by_entities(self, entities: List[HbaseEntity], **options) -> None:
        """
        Deletes the given entities.
        :param entities: must not be null. Must not contain null elements.
        :return:
        """
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            with table.batch(**options) as b:
                for entity in entities:
                    b.delete(entity.id())

    @retry_connection_on_brokenpipe(5)
    def delete_all_by_id(self, ids: List[str], **options) -> None:
        """
        Deletes all instances of the type HbaseEntity with the given IDs.
        Entities that aren't found in the persistence store are silently ignored.
        :param ids: must not be null. Must not contain null elements.
        :return:
        """
        with self.pool.connection() as con:
            table = con.table(self.table_name)
            with table.batch(**options) as b:
                for id in ids:
                    b.delete(id)

    def __create_if_not_exist_table(self, schema: Dict[str,Dict]) -> None:
        """
        Create table with Hbase client  if not exist.
        :param schema: table  schema.
        :return:
        """
        try:
            with self.pool.connection() as con:
                list_tables = con.tables()
                if self.table_name.encode("utf-8") not in list_tables:
                    con.create_table(self.table_name, schema)
        except IOError:
            print("WARN tried to create table BINANCE whereas already created...")