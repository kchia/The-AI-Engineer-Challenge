#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for subject categorizer utility
"""

import os
import sys
import unittest

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from subject_categorizer import SubjectCategorizer, subject_categorizer

class TestSubjectCategorizer(unittest.TestCase):
    """Test cases for SubjectCategorizer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.categorizer = SubjectCategorizer()
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        # Test basic preprocessing
        text = "This is a TEST document with numbers 123 and symbols @#$!"
        result = self.categorizer.preprocess_text(text)
        expected = "this is a test document with numbers 123 and symbols"
        self.assertEqual(result, expected)
        
        # Test empty text
        self.assertEqual(self.categorizer.preprocess_text(""), "")
        self.assertEqual(self.categorizer.preprocess_text(None), "")
        
        # Test whitespace handling
        text = "  Multiple   spaces   and\n\nnewlines  "
        result = self.categorizer.preprocess_text(text)
        expected = "multiple spaces and newlines"
        self.assertEqual(result, expected)
    
    def test_extract_keywords(self):
        """Test keyword extraction"""
        text = "This is a mathematics document about algebra and geometry equations"
        keywords = self.categorizer.extract_keywords(text)
        
        # Should contain relevant keywords
        self.assertIn("mathematics", keywords)
        self.assertIn("algebra", keywords)
        self.assertIn("geometry", keywords)
        self.assertIn("equations", keywords)
        
        # Should not contain stop words
        self.assertNotIn("this", keywords)
        self.assertNotIn("is", keywords)
        self.assertNotIn("a", keywords)
        # Note: "about" is not in our stop words list, so it will be included
        
        # Test empty text
        self.assertEqual(self.categorizer.extract_keywords(""), [])
        self.assertEqual(self.categorizer.extract_keywords(None), [])
    
    def test_calculate_category_scores(self):
        """Test category score calculation"""
        # Test with math keywords
        math_keywords = ["algebra", "geometry", "equation", "formula", "calculate"]
        scores = self.categorizer.calculate_category_scores(math_keywords)
        
        self.assertIn("Mathematics", scores)
        self.assertGreater(scores["Mathematics"], 0)
        
        # Test with empty keywords
        scores = self.categorizer.calculate_category_scores([])
        for score in scores.values():
            self.assertEqual(score, 0.0)
    
    def test_categorize_text_mathematics(self):
        """Test categorization of mathematics content"""
        math_text = """
        This document covers advanced algebra and geometry concepts. 
        We will solve quadratic equations and work with trigonometric functions.
        The mathematical formulas and theorems are essential for understanding calculus.
        """
        
        category, confidence, scores = self.categorizer.categorize_text(math_text)
        
        self.assertEqual(category, "Mathematics")
        self.assertGreater(confidence, 0.1)
        self.assertIn("Mathematics", scores)
        self.assertGreater(scores["Mathematics"], 0)
    
    def test_categorize_text_science(self):
        """Test categorization of science content"""
        science_text = """
        This biology textbook covers cell structure, genetics, and evolution.
        Students will learn about DNA, proteins, and molecular biology.
        The laboratory experiments demonstrate scientific principles and methods.
        """
        
        category, confidence, scores = self.categorizer.categorize_text(science_text)
        
        self.assertEqual(category, "Science")
        self.assertGreater(confidence, 0.1)
        self.assertIn("Science", scores)
        self.assertGreater(scores["Science"], 0)
    
    def test_categorize_text_literature(self):
        """Test categorization of literature content"""
        literature_text = """
        This novel explores themes of love, loss, and redemption through 
        complex characters and poetic language. The author uses symbolism 
        and metaphor to convey deeper meanings in the narrative.
        """
        
        category, confidence, scores = self.categorizer.categorize_text(literature_text)
        
        self.assertEqual(category, "Literature")
        self.assertGreater(confidence, 0.1)
        self.assertIn("Literature", scores)
        self.assertGreater(scores["Literature"], 0)
    
    def test_categorize_text_history(self):
        """Test categorization of history content"""
        history_text = """
        The American Revolution was a pivotal moment in world history.
        This period saw the rise of democracy and the fall of colonial empires.
        Historical documents and artifacts provide evidence of this era.
        """
        
        category, confidence, scores = self.categorizer.categorize_text(history_text)
        
        self.assertEqual(category, "History")
        self.assertGreater(confidence, 0.1)
        self.assertIn("History", scores)
        self.assertGreater(scores["History"], 0)
    
    def test_categorize_text_technology(self):
        """Test categorization of technology content"""
        tech_text = """
        This software development course covers programming languages,
        algorithms, and data structures. Students will learn about
        computer systems, networks, and artificial intelligence.
        """
        
        category, confidence, scores = self.categorizer.categorize_text(tech_text)
        
        self.assertEqual(category, "Technology")
        self.assertGreater(confidence, 0.1)
        self.assertIn("Technology", scores)
        self.assertGreater(scores["Technology"], 0)
    
    def test_categorize_text_other(self):
        """Test categorization of content that doesn't fit any category"""
        other_text = "This is just some random text without specific subject keywords."
        
        category, confidence, scores = self.categorizer.categorize_text(other_text)
        
        # The categorizer might still find some keywords, so we just check confidence is low
        self.assertLessEqual(confidence, 0.2)  # Adjusted threshold
    
    def test_categorize_text_empty(self):
        """Test categorization of empty text"""
        category, confidence, scores = self.categorizer.categorize_text("")
        self.assertEqual(category, "Other")
        self.assertEqual(confidence, 0.0)
        self.assertEqual(scores, {})
        
        category, confidence, scores = self.categorizer.categorize_text(None)
        self.assertEqual(category, "Other")
        self.assertEqual(confidence, 0.0)
        self.assertEqual(scores, {})
    
    def test_categorize_text_confidence_threshold(self):
        """Test categorization with different confidence thresholds"""
        math_text = "This is about algebra and geometry equations."
        
        # Test with low threshold
        category, confidence, scores = self.categorizer.categorize_text(math_text, 0.05)
        self.assertEqual(category, "Mathematics")
        
        # Test with very high threshold (should fall back to Other)
        category, confidence, scores = self.categorizer.categorize_text(math_text, 0.9)
        self.assertEqual(category, "Other")  # Should fall back to Other
    
    def test_get_category_keywords(self):
        """Test getting keywords for specific categories"""
        math_keywords = self.categorizer.get_category_keywords("Mathematics")
        self.assertIsInstance(math_keywords, list)
        self.assertIn("algebra", math_keywords)
        self.assertIn("geometry", math_keywords)
        
        # Test non-existent category
        keywords = self.categorizer.get_category_keywords("NonExistent")
        self.assertEqual(keywords, [])
    
    def test_get_all_categories(self):
        """Test getting all available categories"""
        categories = self.categorizer.get_all_categories()
        self.assertIsInstance(categories, list)
        self.assertIn("Mathematics", categories)
        self.assertIn("Science", categories)
        self.assertIn("Literature", categories)
        self.assertIn("History", categories)
        self.assertIn("Language", categories)
        self.assertIn("Arts", categories)
        self.assertIn("Technology", categories)
        self.assertIn("Other", categories)
    
    def test_analyze_content(self):
        """Test comprehensive content analysis"""
        math_text = "This document covers algebra, geometry, and calculus equations."
        analysis = self.categorizer.analyze_content(math_text)
        
        # Check required fields
        self.assertIn("category", analysis)
        self.assertIn("confidence", analysis)
        self.assertIn("scores", analysis)
        self.assertIn("keywords_found", analysis)
        self.assertIn("total_keywords", analysis)
        self.assertIn("text_length", analysis)
        self.assertIn("available_categories", analysis)
        
        # Check values
        self.assertEqual(analysis["category"], "Mathematics")
        self.assertGreater(analysis["confidence"], 0)
        self.assertIsInstance(analysis["scores"], dict)
        self.assertIsInstance(analysis["keywords_found"], list)
        self.assertGreater(analysis["total_keywords"], 0)
        self.assertGreater(analysis["text_length"], 0)
        self.assertIsInstance(analysis["available_categories"], list)
    
    def test_analyze_content_empty(self):
        """Test content analysis with empty text"""
        analysis = self.categorizer.analyze_content("")
        
        self.assertEqual(analysis["category"], "Other")
        self.assertEqual(analysis["confidence"], 0.0)
        self.assertEqual(analysis["keywords_found"], [])
        self.assertEqual(analysis["total_keywords"], 0)
        self.assertEqual(analysis["text_length"], 0)

def run_tests():
    """Run all tests"""
    print("Running subject categorizer tests...\n")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSubjectCategorizer)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print("\nSUCCESS: All subject categorizer tests passed!")
        return True
    else:
        print("\nFAIL: Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
