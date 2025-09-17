#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Basic tests for file type detection functions
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the functions we want to test
from app import get_file_type, is_supported_file_type, SUPPORTED_FILE_TYPES

def test_get_file_type():
    """Test file type detection from filename"""
    print("Testing get_file_type...")
    
    # Test valid file types
    assert get_file_type("document.pdf") == "PDF Document"
    assert get_file_type("notes.txt") == "Text Document"
    assert get_file_type("essay.docx") == "Word Document"
    assert get_file_type("README.md") == "Markdown Document"
    
    # Test case insensitive
    assert get_file_type("DOCUMENT.PDF") == "PDF Document"
    assert get_file_type("Notes.TXT") == "Text Document"
    
    # Test invalid file types
    assert get_file_type("image.jpg") is None
    assert get_file_type("video.mp4") is None
    assert get_file_type("") is None
    assert get_file_type(None) is None
    
    print("PASS: get_file_type tests passed!")

def test_is_supported_file_type():
    """Test supported file type checking"""
    print("Testing is_supported_file_type...")
    
    # Test supported file types
    assert is_supported_file_type("document.pdf") == True
    assert is_supported_file_type("notes.txt") == True
    assert is_supported_file_type("essay.docx") == True
    assert is_supported_file_type("README.md") == True
    
    # Test case insensitive
    assert is_supported_file_type("DOCUMENT.PDF") == True
    assert is_supported_file_type("Notes.TXT") == True
    
    # Test unsupported file types
    assert is_supported_file_type("image.jpg") == False
    assert is_supported_file_type("video.mp4") == False
    assert is_supported_file_type("") == False
    assert is_supported_file_type(None) == False
    
    print("PASS: is_supported_file_type tests passed!")

def test_supported_file_types_constant():
    """Test SUPPORTED_FILE_TYPES constant"""
    print("Testing SUPPORTED_FILE_TYPES constant...")
    
    expected_types = {
        '.pdf': 'PDF Document',
        '.txt': 'Text Document', 
        '.docx': 'Word Document',
        '.md': 'Markdown Document'
    }
    
    assert SUPPORTED_FILE_TYPES == expected_types
    assert len(SUPPORTED_FILE_TYPES) == 4
    
    print("PASS: SUPPORTED_FILE_TYPES constant tests passed!")

def run_all_tests():
    """Run all tests"""
    print("Running file type detection tests...\n")
    
    try:
        test_supported_file_types_constant()
        test_get_file_type()
        test_is_supported_file_type()
        
        print("\nSUCCESS: All tests passed! File type detection is working correctly.")
        return True
        
    except AssertionError as e:
        print("\nFAIL: Test failed: {}".format(e))
        return False
    except Exception as e:
        print("\nERROR: Test error: {}".format(e))
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
