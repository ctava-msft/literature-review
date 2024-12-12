from dotenv import load_dotenv
load_dotenv()

import unittest
from unittest.mock import patch, MagicMock
import query

class TestQueryModule(unittest.TestCase):

    @patch('query.os.getenv')
    def test_generate_embeddings(self, mock_getenv):
        mock_getenv.return_value = 'dummy_value'
        with patch('query.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'data': [{'embedding': [0.1, 0.2, 0.3]}]
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            embedding = query.generate_embeddings('test text')
            self.assertEqual(embedding, [0.1, 0.2, 0.3])

    @patch('query.AzureKeyCredential')
    @patch('query.SearchClient')
    @patch('query.generate_embeddings')
    def test_query_azure_search(self, mock_generate_embeddings, mock_search_client, mock_credential):
        mock_generate_embeddings.return_value = [0.1, 0.2, 0.3]
        mock_client_instance = MagicMock()
        mock_search_client.return_value = mock_client_instance
        mock_client_instance.search.return_value = []

        results = query.query_azure_search('test query')
        self.assertIsInstance(results, list)

    @patch('query.os.getenv')
    def test_query_azure_openai(self, mock_getenv):
        mock_getenv.return_value = 'dummy_value'
        with patch('query.requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                'choices': [{
                    'message': {'content': 'This is a test response.'}
                }]
            }
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response

            answer = query.query_azure_openai('test prompt', [])
            self.assertEqual(answer, 'This is a test response.')

    @patch('query.open')
    @patch('query.random.randint')
    def test_save_to_markdown(self, mock_randint, mock_open):
        mock_randint.return_value = 1234
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        query.save_to_markdown('test query', [], [], 'test answer')
        mock_file.write.assert_called()

if __name__ == '__main__':
    unittest.main()