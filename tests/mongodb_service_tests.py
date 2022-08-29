import unittest
from unittest.mock import MagicMock
from db_services.mongodb_service import MongodbService


class MongoDbServiceTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.db_service = MongodbService(self.client)

    def test_isDbExist_dbDoesNotExist_False(self):
        self.client.list_database_names.return_value = ['exists1', 'exists2']
        result = self.db_service.is_db_exist('DoesNotExist')
        self.assertFalse(result)

    def test_isDbExist_dbExist_True(self):
        self.client.list_database_names.return_value = ['exists1', 'exists2']
        result = self.db_service.is_db_exist('exists1')
        self.assertTrue(result)

    def test_isCollectionExist_CollectionDoesNotExist_False(self):
        db_mock = self.client['exist']
        db_mock.list_collection_names.return_value = ['exist1', 'exist2']
        result = self.db_service.is_collection_exist('exist', 'not_exist_collection')
        self.assertFalse(result)

    def test_isCollectionExist_CollectionExist_True(self):
        db_mock = self.client['exist']
        db_mock.list_collection_names.return_value = ['exist1', 'exist2']
        result = self.db_service.is_collection_exist('exist', 'exist1')
        self.assertTrue(result)

    def test_getCollection_dbAndCollectionExist_Success(self):
        self.client.list_database_names.return_value = ['db_exist']
        db_mock = self.client['db_exist']
        db_mock.list_collection_names.return_value = ['collection_exist', 'exist2']
        collection_mock = db_mock['collection_exist']
        collection_mock.return_value = 'collection_exist'
        result = self.db_service.get_collection('db_exist', 'collection_exist')
        self.assertEqual(result.return_value, 'collection_exist')

    def test_getCollection_dbExistCollectionDoesNotExist_Failure(self):
        db_name = 'db_exist'
        collection_name = 'collection_does_not_exist'
        self.client.list_database_names.return_value = [db_name]
        db_mock = self.client[db_name]
        db_mock.list_collection_names.return_value = ['collection_exist']
        collection_mock = db_mock['collection_exist']
        collection_mock.return_value = 'collection_exist'
        with self.assertRaisesRegex(KeyError,
                                    f'collection: {collection_name} does not exist under database: {db_name}'):
            self.db_service.get_collection(db_name, collection_name)

    def test_getCollection_dbDoesNotExist_Failure(self):
        db_name = 'db_does_not_exist'
        self.client.list_database_names.return_value = ['db_exist']
        with self.assertRaisesRegex(KeyError,
                                    f'database: {db_name} does not exist under client: {self.client}'):
            self.db_service.get_collection(db_name, 'collection_exist')


if __name__ == '__main__':
    unittest.main()
