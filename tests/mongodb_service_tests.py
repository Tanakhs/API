import unittest
from bson.objectid import ObjectId
from unittest.mock import MagicMock
from db_services.mongodb_service import MongodbService
from pymongo.results import UpdateResult, DeleteResult

DB_EXIST_NAME = "db_exist"
DB_NOT_EXIST_NAME = "db_does_not_exist"
COLLECTION_NAME_EXIST = "collection_exist"
COLLECTION_DOES_NOT_EXIST = "collection_does_not_exist"


class MongoDbServiceTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.db_service = MongodbService(self.client)
        self.db_mock, self.collection_mock = self.mock_behaviour()

    def test_is_db_Exist_db_does_not_exist_false(self):
        result = self.db_service.is_db_exist(DB_NOT_EXIST_NAME)
        self.assertFalse(result)

    def test_is_db_exist_db_exist_true(self):
        result = self.db_service.is_db_exist(DB_EXIST_NAME)
        self.assertTrue(result)

    def test_is_collection_exist_collection_does_not_exist_false(self):
        result = self.db_service.is_collection_exist(DB_EXIST_NAME, COLLECTION_DOES_NOT_EXIST)
        self.assertFalse(result)

    def test_is_collection_exist_collection_exist_true(self):
        result = self.db_service.is_collection_exist(DB_EXIST_NAME, COLLECTION_NAME_EXIST)
        self.assertTrue(result)

    def test_get_collection_db_and_collection_exist_success(self):
        # arrange
        self.collection_mock.return_value = COLLECTION_NAME_EXIST
        # act
        result = self.db_service.get_collection(DB_EXIST_NAME, COLLECTION_NAME_EXIST)
        # assert
        self.assertEqual(result.return_value, COLLECTION_NAME_EXIST)

    def test_get_collection_db_exist_collection_does_not_exist_failure(self):
        with self.assertRaisesRegex(KeyError,
                                    f"collection: {COLLECTION_DOES_NOT_EXIST} does not exist under database: {DB_EXIST_NAME}"):
            self.db_service.get_collection(DB_EXIST_NAME, COLLECTION_DOES_NOT_EXIST)

    def test_get_collection_db_does_not_exist_failure(self):
        with self.assertRaisesRegex(KeyError,
                                    f"database: {DB_NOT_EXIST_NAME} does not exist under client: {self.client}"):
            self.db_service.get_collection(DB_NOT_EXIST_NAME, COLLECTION_NAME_EXIST)

    def test_find_one_exist_success(self):
        record = {"key": ""}
        self.collection_mock.find_one.return_value = record
        result = self.db_service.find_one(DB_EXIST_NAME, COLLECTION_NAME_EXIST, record)
        self.assertEqual(result, record)

    def test_find_one_does_not_exist_failure(self):
        record = {}
        self.collection_mock.find_one.return_value = record
        result = self.db_service.find_one(DB_EXIST_NAME, COLLECTION_NAME_EXIST, {"key": "eli_is_king!"})
        self.assertEqual(result, record)

    def test_find_exist_success(self):
        record = {"key1": "some_id_1",
                  "key2": "some_id_2"}
        self.collection_mock.find.return_value = record
        result = self.db_service.find(DB_EXIST_NAME, COLLECTION_NAME_EXIST, record)
        self.assertEqual(result, record)

    def test_find_does_not_exist_failure(self):
        record = {}
        self.collection_mock.find.return_value = record
        result = self.db_service.find(DB_EXIST_NAME, COLLECTION_NAME_EXIST, {"key1": "some_id_1",
                                                                             "key2": "some_id_2"})
        self.assertEqual(result, record)

    def test_insert_one_success(self):
        record = {"key1": "some_id_1",
                  "key2": "some_id_2"}
        insert_one_result = self.collection_mock.insert_one.return_value
        insert_one_result.inserted_id = ObjectId()
        result = self.db_service.insert_one(DB_EXIST_NAME, COLLECTION_NAME_EXIST, record)
        self.assertIsInstance(result, ObjectId)

    def test_insert_one_failure(self):
        record = {"key1": "some_id_1",
                  "key2": "some_id_2"}
        result = self.db_service.insert_one(DB_EXIST_NAME, COLLECTION_NAME_EXIST, record)
        self.assertNotIsInstance(result, ObjectId)

    def test_update_one_success(self):
        record = {"key1": "some_id_1",
                  "key2": "some_id_2"}
        update_one_result = self.collection_mock.update_one.return_value
        update_one_result.matched_count = 1
        result = self.db_service.update_one(DB_EXIST_NAME, COLLECTION_NAME_EXIST, {}, {})
        self.assertEqual(result.matched_count, 1)

    def test_update_one_failure(self):
        update_one_result = self.collection_mock.update_one.return_value
        update_one_result.matched_count = 0
        result = self.db_service.update_one(DB_EXIST_NAME, COLLECTION_NAME_EXIST, {}, {})
        self.assertEqual(result.matched_count, 0)

    def test_delete_one_success(self):
        delete_one_result = self.collection_mock.delete_one.return_value
        delete_one_result.deleted_count = 1
        result = self.db_service.delete_one(DB_EXIST_NAME, COLLECTION_NAME_EXIST, {})
        self.assertEqual(result.deleted_count, 1)

    def test_delete_one_failure(self):  # use cases: db/collection/record not found
        delete_one_result = self.collection_mock.delete_one.return_value
        delete_one_result.deleted_count = 0
        result = self.db_service.delete_one(DB_EXIST_NAME, COLLECTION_NAME_EXIST, {})
        self.assertEqual(result.deleted_count, 0)

    def mock_behaviour(self):
        """db&collection_exist hold their relative names"""
        self.client.list_database_names.return_value = [DB_EXIST_NAME]
        db_mock = self.client[DB_EXIST_NAME]
        db_mock.list_collection_names.return_value = COLLECTION_NAME_EXIST
        collection_mock = db_mock[COLLECTION_NAME_EXIST]
        return db_mock, collection_mock


if __name__ == '__main__':
    unittest.main()
