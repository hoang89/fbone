__author__ = 'hoangnn'
from tests import TestCase
from fbone.reader.models import Reader
from fbone.reader.constant import ANDROID
from mock import patch, Mock
from unittest import expectedFailure

class TestReaderModel(TestCase):

    def create_model(self):
        reader = Reader()
        reader.uuid = "uuid_of_device"
        reader.device_token = "token_of_device"
        reader.os = ANDROID
        return reader

    def setUp(self):
        self.model = self.create_model()

    def test_create_model(self):
        model = self.model
        self.assertIsNotNone(model.uuid)
        self.assertIsNotNone(model.device_token)
        self.assertIsNotNone(model.os)

    @patch.object(Reader, "getByUUID")
    def test_get_by_uuid(self, getByUUIDMock):
        model = self.model
        getByUUIDMock.return_value = model, False
        reader = Reader.getOrCreate(uuid=model.uuid, os=model.os, token=model.device_token)
        getByUUIDMock.assert_called_once_with(uuid=model.uuid)
        self.assertEqual(model,reader)

    @patch.object(Reader, "save")
    @patch.object(Reader, "getByUUID")
    def test_save_call(self,getByUUIDMock, saveMock):
        model = self.model
        getByUUIDMock.return_value = model, True
        Reader.getOrCreate(uuid=model.uuid, os=model.os, token=model.device_token)
        saveMock.assert_called_once_with()

    @expectedFailure
    @patch.object(Reader, "save")
    @patch.object(Reader, "getByUUID")
    def test_save_not_call(self,getByUUIDMock, saveMock):
        model = self.model
        getByUUIDMock.return_value = model, False
        Reader.getOrCreate(uuid=model.uuid, os=model.os, token=model.device_token)
        saveMock.assert_called_once_with()

    def test_save_to_database(self):
        model = self.model
        Reader.getOrCreate(uuid=model.uuid, os=model.os, token=model.device_token)
        self.assertIsNotNone(Reader.objects.first())

    def tearDown(self):
        Reader.drop_collection()
        self.model = None