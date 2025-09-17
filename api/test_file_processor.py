#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for file processor utility
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from file_processor import FileProcessor, file_processor

class TestFileProcessor(unittest.TestCase):
    """Test cases for FileProcessor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = FileProcessor()
        self.test_text = "This is a test document with educational content. " * 50
    
    def test_is_supported_file(self):
        """Test file type support checking"""
        # Test supported files
        self.assertTrue(self.processor.is_supported_file("document.pdf"))
        self.assertTrue(self.processor.is_supported_file("notes.txt"))
        self.assertTrue(self.processor.is_supported_file("essay.docx"))
        self.assertTrue(self.processor.is_supported_file("README.md"))
        
        # Test case insensitive
        self.assertTrue(self.processor.is_supported_file("DOCUMENT.PDF"))
        self.assertTrue(self.processor.is_supported_file("Notes.TXT"))
        
        # Test unsupported files
        self.assertFalse(self.processor.is_supported_file("image.jpg"))
        self.assertFalse(self.processor.is_supported_file("video.mp4"))
        self.assertFalse(self.processor.is_supported_file(""))
        self.assertFalse(self.processor.is_supported_file(None))
    
    def test_get_file_extension(self):
        """Test file extension extraction"""
        self.assertEqual(self.processor.get_file_extension("document.pdf"), ".pdf")
        self.assertEqual(self.processor.get_file_extension("notes.txt"), ".txt")
        self.assertEqual(self.processor.get_file_extension("essay.docx"), ".docx")
        self.assertEqual(self.processor.get_file_extension("README.md"), ".md")
        self.assertEqual(self.processor.get_file_extension(""), "")
        self.assertEqual(self.processor.get_file_extension(None), "")
    
    def test_validate_file_size(self):
        """Test file size validation"""
        # Test valid size
        small_content = b"small content"
        self.processor.validate_file_size(small_content)
        
        # Test too large
        large_content = b"x" * (self.processor.max_file_size + 1)
        with self.assertRaises(Exception):  # HTTPException
            self.processor.validate_file_size(large_content)
    
    def test_extract_text_from_txt(self):
        """Test text extraction from TXT files"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.test_text)
            temp_path = f.name
        
        try:
            result = self.processor.extract_text_from_txt(temp_path)
            self.assertEqual(result, self.test_text)
        finally:
            os.unlink(temp_path)
    
    def test_extract_text_from_txt_empty(self):
        """Test text extraction from empty TXT file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            with self.assertRaises(Exception):  # HTTPException
                self.processor.extract_text_from_txt(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_extract_text_from_md(self):
        """Test text extraction from Markdown files"""
        markdown_content = "# Test Document\n\nThis is **bold** and *italic* text."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(markdown_content)
            temp_path = f.name
        
        try:
            result = self.processor.extract_text_from_md(temp_path)
            self.assertEqual(result, markdown_content)
        finally:
            os.unlink(temp_path)
    
    @patch('file_processor.AIMAKERSPACE_AVAILABLE', True)
    @patch('file_processor.PDFLoader')
    def test_extract_text_from_pdf(self, mock_pdf_loader):
        """Test text extraction from PDF files"""
        # Mock PDF loader
        mock_loader_instance = MagicMock()
        mock_loader_instance.documents = [self.test_text]
        mock_pdf_loader.return_value = mock_loader_instance
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"fake pdf content")
            temp_path = f.name
        
        try:
            result = self.processor.extract_text_from_pdf(temp_path)
            self.assertEqual(result, self.test_text)
        finally:
            os.unlink(temp_path)
    
    @patch('file_processor.AIMAKERSPACE_AVAILABLE', False)
    def test_extract_text_from_pdf_no_aimakerspace(self):
        """Test PDF extraction when aimakerspace is not available"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b"fake pdf content")
            temp_path = f.name
        
        try:
            with self.assertRaises(Exception):  # HTTPException
                self.processor.extract_text_from_pdf(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_extract_text_from_docx(self):
        """Test text extraction from DOCX files"""
        # Test with mock docx module
        with patch.dict('sys.modules', {'docx': MagicMock()}):
            from docx import Document
            
            # Mock DOCX document
            mock_doc = MagicMock()
            mock_paragraph = MagicMock()
            mock_paragraph.text = "Test paragraph"
            mock_doc.paragraphs = [mock_paragraph]
            Document.return_value = mock_doc
            
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
                f.write(b"fake docx content")
                temp_path = f.name
            
            try:
                result = self.processor.extract_text_from_docx(temp_path)
                self.assertEqual(result, "Test paragraph")
            finally:
                os.unlink(temp_path)
    
    def test_extract_text_from_docx_no_module(self):
        """Test DOCX extraction when docx module is not available"""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            f.write(b"fake docx content")
            temp_path = f.name
        
        try:
            # Mock the import to raise ImportError
            with patch('builtins.__import__', side_effect=ImportError("No module named 'docx'")):
                with self.assertRaises(Exception):  # HTTPException
                    self.processor.extract_text_from_docx(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_extract_text_unsupported_file(self):
        """Test text extraction with unsupported file type"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(b"fake image content")
            temp_path = f.name
        
        try:
            with self.assertRaises(Exception):  # HTTPException
                self.processor.extract_text(temp_path, "image.jpg")
        finally:
            os.unlink(temp_path)
    
    def test_split_text_into_chunks(self):
        """Test text chunking functionality"""
        # Test with aimakerspace available
        with patch('file_processor.AIMAKERSPACE_AVAILABLE', True):
            with patch('file_processor.CharacterTextSplitter') as mock_splitter:
                mock_splitter_instance = MagicMock()
                mock_splitter_instance.split.return_value = ["chunk1", "chunk2", "chunk3"]
                mock_splitter.return_value = mock_splitter_instance
                
                chunks = self.processor.split_text_into_chunks(self.test_text)
                self.assertEqual(len(chunks), 3)
        
        # Test without aimakerspace (fallback)
        with patch('file_processor.AIMAKERSPACE_AVAILABLE', False):
            chunks = self.processor.split_text_into_chunks(self.test_text)
            self.assertIsInstance(chunks, list)
            self.assertGreater(len(chunks), 0)
    
    def test_process_file(self):
        """Test complete file processing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.test_text)
            temp_path = f.name
        
        try:
            with open(temp_path, 'rb') as f:
                content = f.read()
            
            text_content, chunks = self.processor.process_file(content, "test.txt")
            
            self.assertEqual(text_content, self.test_text)
            self.assertIsInstance(chunks, list)
            self.assertGreater(len(chunks), 0)
        finally:
            os.unlink(temp_path)
    
    def test_process_file_unsupported(self):
        """Test processing unsupported file type"""
        content = b"fake content"
        
        with self.assertRaises(Exception):  # HTTPException
            self.processor.process_file(content, "image.jpg")
    
    def test_process_file_too_large(self):
        """Test processing file that's too large"""
        large_content = b"x" * (self.processor.max_file_size + 1)
        
        with self.assertRaises(Exception):  # HTTPException
            self.processor.process_file(large_content, "large.txt")

def run_tests():
    """Run all tests"""
    print("Running file processor tests...\n")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFileProcessor)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print("\nSUCCESS: All file processor tests passed!")
        return True
    else:
        print("\nFAIL: Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
