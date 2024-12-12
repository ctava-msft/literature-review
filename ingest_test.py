import unittest
from unittest.mock import patch, MagicMock
from ingest import extract_text_from_pdf, extract_text_from_docx

class TestIngest(unittest.TestCase):

    @patch('fitz.open')
    def test_extract_text_from_pdf(self, mock_fitz_open):
        mock_pdf = MagicMock()
        mock_pdf.__enter__.return_value = mock_pdf
        mock_pdf.__len__.return_value = 1
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample PDF text."
        mock_pdf.load_page.return_value = mock_page
        mock_fitz_open.return_value = mock_pdf

        text = extract_text_from_pdf("dummy.pdf")
        self.assertEqual(text, "Sample PDF text.")

    @patch('docx.Document')
    def test_extract_text_from_docx(self, mock_Document):
        mock_doc = MagicMock()
        mock_paragraph = MagicMock()
        mock_paragraph.text = "Sample DOCX text."
        mock_doc.paragraphs = [mock_paragraph]
        mock_Document.return_value = mock_doc

        text = extract_text_from_docx("dummy.docx")
        self.assertEqual(text, "Sample DOCX text.")

if __name__ == '__main__':
    unittest.main()