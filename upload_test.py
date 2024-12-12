import unittest
from unittest.mock import patch, MagicMock
from upload import upload_files


class TestUploadFiles(unittest.TestCase):
    @patch('upload.os.getenv')
    @patch('upload.requests.get')
    @patch('upload.BlobServiceClient')
    def test_upload_files(self, mock_blob_service_client, mock_requests_get, mock_os_getenv):
        # Mock environment variables
        mock_os_getenv.side_effect = lambda var: {
            'AZURE_STORAGE_ACCOUNT': 'test_account',
            'AZURE_STORAGE_ACCOUNT_KEY': 'test_key',
            'AZURE_STORAGE_CONTAINER': 'test_container',
            'BLOB_NAME': 'test_blob',
            'PUBLIC_URL': 'http://testurl.com'
        }.get(var, None)

        # Mock requests.get
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_requests_get.return_value = mock_response

        # Mock BlobServiceClient
        mock_blob_service_client_instance = MagicMock()
        mock_container_client_instance = MagicMock()
        mock_blob_service_client.from_connection_string.return_value = mock_blob_service_client_instance
        mock_blob_service_client_instance.get_container_client.return_value = mock_container_client_instance
        mock_blob_client_instance = MagicMock()
        mock_container_client_instance.get_blob_client.return_value = mock_blob_client_instance

        # Mock file opening and reading
        test_file_path = 'test_file.txt'
        with open(test_file_path, 'w') as f:
            f.write('Test content')

        # Call the function
        upload_files(test_file_path)

        # Assertions
        mock_requests_get.assert_called_once_with('http://testurl.com', verify=False)
        mock_blob_client_instance.upload_blob.assert_called_once()