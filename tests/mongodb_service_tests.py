import unittest
from unittest.mock import Mock
from db_services.mongodb_service import MongodbService


class MongoDbServiceTests(unittest.TestCase):
    def setUp(self):
        self.client = Mock()
        self.db_service = MongodbService(self.client)

    def test_isDbExist_dbDoesNotExist_False(self):
        self.client.list_database_names.return_value = ["exists1", "exists2"]
        result = self.db_service.is_db_exist("DoesNotExist")
        self.assertFalse(result)

    def test_isDbExist_dbExist_False(self):
        self.client.list_database_names.return_value = ["exists1", "exists2"]
        result = self.db_service.is_db_exist("exists1")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
