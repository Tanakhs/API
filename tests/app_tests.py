import json
import os
import unittest
from flask_jwt_extended import create_access_token
from app import app
from unittest import mock
from tests.test_data.mock_data import *


def mock_request_info(mock_data_func):
    access_token = create_access_token('test')
    headers = {
        'Authorization': 'Bearer {}'.format(access_token)
    }
    data = mock_data_func()
    user = {
        'user_name': 'test',
        'password': 'testpassword',
        'role': 'admin',
        'profile_picture_url': 'https://www.shutterstock.com/image-vector/man-icon-vector-260nw-1040084344.jpg',
        'email_address': 'test@gmail.com',
        'age': 25,
        'gender': 'other',
        'religion': 'atheist',
    }

    return headers, data, user


class AppTests(unittest.TestCase):
    def setUp(self):
        app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY_TEST']
        self._client = app.test_client()

    @mock.patch('app._db_controller')
    def test_getChapters_success(self, mock_db_controller):
        mock_db_controller.find.return_value = mock_chapters_data()
        result = self._client.get('/api/v1/chapters')
        self.assertEqual(200, result.status_code)
        self.assertGreater(len(result.data), 0)

    @mock.patch('app._db_controller')
    def test_getChapter_success(self, mock_db_controller):
        mock_db_controller.find_one.return_value = mock_chapter_data()
        result = self._client.get(f'/api/v1/chapter/{ObjectId()}')
        self.assertEqual(200, result.status_code)
        self.assertGreater(len(result.data), 0)

    @mock.patch('app._db_controller')
    def test_getChapter_failure(self, mock_db_controller):
        mock_db_controller.find_one.return_value = None
        result = self._client.get(f'/api/v1/chapter/{ObjectId()}')
        self.assertEqual(404, result.status_code)

    @mock.patch('app._db_controller')
    def test_updateChapter_success(self, mock_db_controller):
        with app.app_context():
            headers, data, user = mock_request_info(mock_chapter_data)
            mock_db_controller.find_one.return_value = user
            update_one_result = mock_db_controller.update_one.return_value
            update_one_result.matched_count = 1
            result = self._client.put(f'/api/v1/chapter/{str(ObjectId())}', headers=headers, data=json.dumps(data),
                                      content_type='application/json',
                                      )
        self.assertEqual(202, result.status_code)

    @mock.patch('app._db_controller')
    def test_updateChapter_failure(self, mock_db_controller):
        with app.app_context():
            headers, data, user = mock_request_info(mock_chapter_data)
            mock_db_controller.find_one.return_value = user
            update_one_result = mock_db_controller.update_one.return_value
            update_one_result.matched_count = 0
            result = self._client.put(f'/api/v1/chapter/{str(ObjectId())}', headers=headers, data=json.dumps(data),
                                      content_type='application/json',
                                      )
        self.assertEqual(404, result.status_code)

    @mock.patch('app._db_controller')
    def test_postChapter_success(self, mock_db_controller):
        with app.app_context():
            headers, data, user = mock_request_info(mock_chapter_data)
            mock_db_controller.find_one.return_value = user
            insert_one_result = mock_db_controller.insert_one.return_value
            insert_one_result.return_value = ObjectId()
            result = self._client.post(f'/api/v1/chapter', headers=headers, data=json.dumps(data),
                                       content_type='application/json',
                                       )
        self.assertEqual(201, result.status_code)

    @mock.patch('app._db_controller')
    def test_postChapter_failure(self, mock_db_controller):
        with app.app_context():
            headers, data, user = mock_request_info(mock_chapter_data)
            mock_db_controller.find_one.return_value = user
            mock_db_controller.insert_one.return_value = None
            result = self._client.post(f'/api/v1/chapter', headers=headers, data=json.dumps(data),
                                       content_type='application/json',
                                       )
        self.assertEqual(500, result.status_code)

    @mock.patch('app._db_controller')
    def test_postComment_success(self, mock_db_controller):
        with app.app_context():
            headers, data, user = mock_request_info(mock_comment_data)
            mock_db_controller.find_one.return_value = user
            update_one_result = mock_db_controller.update_one.return_value
            update_one_result.matched_count = 1
            result = self._client.post(f'/api/v1/comment/62fbacd709932fd2b4d682a4', headers=headers,
                                       data=json.dumps(data),
                                       content_type='application/json',
                                       )
        self.assertEqual(202, result.status_code)

    @mock.patch('app._db_controller')
    def test_postComment_failure(self, mock_db_controller):
        with app.app_context():
            headers, data, user = mock_request_info(mock_comment_data)
            mock_db_controller.find_one.return_value = user
            update_one_result = mock_db_controller.update_one.return_value
            update_one_result.matched_count = 0
            result = self._client.post(f'/api/v1/comment/62fbacd709932fd2b4d682a4', headers=headers,
                                       data=json.dumps(data),
                                       content_type='application/json',
                                       )
        self.assertEqual(404, result.status_code)


if __name__ == '__main__':
    unittest.main()
