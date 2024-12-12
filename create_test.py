import unittest
from unittest.mock import patch, MagicMock
from create import create_file_index

class TestCreateFileIndex(unittest.TestCase):
    @patch('create.SearchIndexClient')
    @patch('create.AzureKeyCredential')
    @patch('create.os.getenv')
    def test_create_file_index(self, mock_getenv, mock_credential, mock_search_client):
        # Mock environment variables
        mock_getenv.side_effect = lambda var: 'test_value'

        # Mock AzureKeyCredential and SearchIndexClient
        mock_search_client_instance = mock_search_client.return_value
        mock_search_client_instance.create_or_update_index.return_value = None

        # Call the function
        create_file_index()

        # Assert that create_or_update_index was called
        mock_search_client_instance.create_or_update_index.assert_called_once()

if __name__ == '__main__':
    unittest.main()