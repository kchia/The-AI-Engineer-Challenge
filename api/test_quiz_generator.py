#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for quiz generator utility
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from quiz_generator import QuizGenerator, create_quiz_generator

class TestQuizGenerator(unittest.TestCase):
    """Test cases for QuizGenerator class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api_key = "test-api-key"
        self.generator = QuizGenerator(self.api_key)
        self.sample_content = """
        This is a sample educational content about mathematics.
        It covers topics like algebra, geometry, and calculus.
        Students will learn about equations, formulas, and mathematical proofs.
        The content includes examples and practice problems.
        """
    
    def test_init(self):
        """Test QuizGenerator initialization"""
        generator = QuizGenerator("test-key")
        self.assertEqual(generator.client.api_key, "test-key")
        self.assertIsInstance(generator.question_types, list)
        self.assertIn("multiple_choice", generator.question_types)
    
    def test_create_quiz_generator(self):
        """Test factory function"""
        generator = create_quiz_generator("test-key")
        self.assertIsInstance(generator, QuizGenerator)
        self.assertEqual(generator.client.api_key, "test-key")
    
    def test_generate_quiz_prompt(self):
        """Test quiz prompt generation"""
        prompt = self.generator.generate_quiz_prompt(self.sample_content, 3, ["multiple_choice"])
        
        self.assertIn("sample educational content", prompt)
        self.assertIn("3", prompt)
        self.assertIn("multiple_choice", prompt)
        self.assertIn("JSON", prompt)
    
    def test_generate_quiz_prompt_defaults(self):
        """Test quiz prompt with default parameters"""
        prompt = self.generator.generate_quiz_prompt(self.sample_content)
        
        self.assertIn("5", prompt)  # Default num_questions
        self.assertIn("multiple_choice", prompt)  # Default question types
        self.assertIn("true_false", prompt)
    
    @patch('quiz_generator.OpenAI')
    def test_generate_quiz_success(self, mock_openai):
        """Test successful quiz generation"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "title": "Mathematics Quiz",
            "description": "Test your math knowledge",
            "questions": [
                {
                    "id": 1,
                    "type": "multiple_choice",
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5", "6"],
                    "correct_answer": "4",
                    "explanation": "2 + 2 equals 4",
                    "difficulty": "easy"
                }
            ],
            "total_questions": 1,
            "estimated_time": "5 minutes"
        }
        '''
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create a new generator with mocked client
        generator = QuizGenerator("test-key")
        generator.client = mock_client
        
        # Test quiz generation
        quiz = generator.generate_quiz(self.sample_content, 1, ["multiple_choice"])
        
        self.assertEqual(quiz["title"], "Mathematics Quiz")
        self.assertEqual(len(quiz["questions"]), 1)
        self.assertEqual(quiz["questions"][0]["type"], "multiple_choice")
        self.assertEqual(quiz["questions"][0]["correct_answer"], "4")
    
    def test_generate_quiz_invalid_content(self):
        """Test quiz generation with invalid content"""
        with self.assertRaises(ValueError):
            self.generator.generate_quiz("", 5)
        
        with self.assertRaises(ValueError):
            self.generator.generate_quiz(None, 5)
    
    def test_generate_quiz_invalid_num_questions(self):
        """Test quiz generation with invalid number of questions"""
        with self.assertRaises(ValueError):
            self.generator.generate_quiz(self.sample_content, 0)
        
        with self.assertRaises(ValueError):
            self.generator.generate_quiz(self.sample_content, 11)
    
    def test_generate_quiz_invalid_question_types(self):
        """Test quiz generation with invalid question types"""
        with self.assertRaises(ValueError):
            self.generator.generate_quiz(self.sample_content, 5, ["invalid_type"])
    
    def test_validate_quiz_structure_valid(self):
        """Test quiz structure validation with valid data"""
        valid_quiz = {
            "title": "Test Quiz",
            "description": "A test quiz",
            "questions": [
                {
                    "id": 1,
                    "type": "multiple_choice",
                    "question": "What is 2 + 2?",
                    "options": ["3", "4", "5"],
                    "correct_answer": "4",
                    "explanation": "2 + 2 = 4",
                    "difficulty": "easy"
                }
            ],
            "total_questions": 1
        }
        
        # Should not raise an exception
        self.generator._validate_quiz_structure(valid_quiz, 1)
    
    def test_validate_quiz_structure_missing_fields(self):
        """Test quiz structure validation with missing fields"""
        invalid_quiz = {
            "title": "Test Quiz",
            # Missing description, questions, total_questions
        }
        
        with self.assertRaises(ValueError):
            self.generator._validate_quiz_structure(invalid_quiz, 1)
    
    def test_validate_quiz_structure_wrong_question_count(self):
        """Test quiz structure validation with wrong question count"""
        quiz = {
            "title": "Test Quiz",
            "description": "A test quiz",
            "questions": [{"id": 1}],  # Only 1 question
            "total_questions": 1
        }
        
        with self.assertRaises(ValueError):
            self.generator._validate_quiz_structure(quiz, 2)  # Expecting 2 questions
    
    def test_validate_question_valid(self):
        """Test question validation with valid question"""
        valid_question = {
            "id": 1,
            "type": "multiple_choice",
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5"],
            "correct_answer": "4",
            "explanation": "2 + 2 = 4",
            "difficulty": "easy"
        }
        
        # Should not raise an exception
        self.generator._validate_question(valid_question, 1)
    
    def test_validate_question_missing_fields(self):
        """Test question validation with missing fields"""
        invalid_question = {
            "id": 1,
            "type": "multiple_choice",
            # Missing other required fields
        }
        
        with self.assertRaises(ValueError):
            self.generator._validate_question(invalid_question, 1)
    
    def test_validate_question_invalid_type(self):
        """Test question validation with invalid type"""
        invalid_question = {
            "id": 1,
            "type": "invalid_type",
            "question": "What is 2 + 2?",
            "correct_answer": "4",
            "explanation": "2 + 2 = 4",
            "difficulty": "easy"
        }
        
        with self.assertRaises(ValueError):
            self.generator._validate_question(invalid_question, 1)
    
    def test_validate_question_multiple_choice_missing_options(self):
        """Test question validation for multiple choice without options"""
        invalid_question = {
            "id": 1,
            "type": "multiple_choice",
            "question": "What is 2 + 2?",
            "correct_answer": "4",
            "explanation": "2 + 2 = 4",
            "difficulty": "easy"
            # Missing options
        }
        
        with self.assertRaises(ValueError):
            self.generator._validate_question(invalid_question, 1)
    
    def test_validate_question_true_false_invalid_answer(self):
        """Test question validation for true/false with invalid answer"""
        invalid_question = {
            "id": 1,
            "type": "true_false",
            "question": "Is 2 + 2 = 4?",
            "correct_answer": "yes",  # Should be boolean
            "explanation": "2 + 2 = 4",
            "difficulty": "easy"
        }
        
        with self.assertRaises(ValueError):
            self.generator._validate_question(invalid_question, 1)
    
    def test_validate_question_invalid_difficulty(self):
        """Test question validation with invalid difficulty"""
        invalid_question = {
            "id": 1,
            "type": "multiple_choice",
            "question": "What is 2 + 2?",
            "options": ["3", "4", "5"],
            "correct_answer": "4",
            "explanation": "2 + 2 = 4",
            "difficulty": "very_hard"  # Invalid difficulty
        }
        
        with self.assertRaises(ValueError):
            self.generator._validate_question(invalid_question, 1)
    
    @patch('quiz_generator.OpenAI')
    def test_generate_study_guide_success(self, mock_openai):
        """Test successful study guide generation"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices[0].message.content = '''
        {
            "title": "Mathematics Study Guide",
            "subject": "Mathematics",
            "key_concepts": ["Algebra", "Geometry", "Calculus"],
            "important_points": ["Practice regularly", "Understand concepts"],
            "study_tips": ["Use flashcards", "Solve practice problems"],
            "practice_questions": ["What is 2 + 2?", "Solve for x: 2x = 4"],
            "summary": "This guide covers basic mathematics concepts",
            "estimated_study_time": "30 minutes"
        }
        '''
        
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        # Create a new generator with mocked client
        generator = QuizGenerator("test-key")
        generator.client = mock_client
        
        # Test study guide generation
        guide = generator.generate_study_guide(self.sample_content, "Mathematics")
        
        self.assertEqual(guide["title"], "Mathematics Study Guide")
        self.assertEqual(guide["subject"], "Mathematics")
        self.assertIn("Algebra", guide["key_concepts"])
        self.assertIn("Practice regularly", guide["important_points"])
    
    def test_generate_study_guide_invalid_content(self):
        """Test study guide generation with invalid content"""
        with self.assertRaises(ValueError):
            self.generator.generate_study_guide("", "Mathematics")
        
        with self.assertRaises(ValueError):
            self.generator.generate_study_guide(None, "Mathematics")
    
    def test_get_available_question_types(self):
        """Test getting available question types"""
        types = self.generator.get_available_question_types()
        
        self.assertIsInstance(types, list)
        self.assertIn("multiple_choice", types)
        self.assertIn("true_false", types)
        self.assertIn("short_answer", types)
        self.assertIn("fill_blank", types)
    
    def test_estimate_quiz_time(self):
        """Test quiz time estimation"""
        # Test with different question types
        time = self.generator.estimate_quiz_time(5, ["multiple_choice"])
        self.assertIn("minutes", time)
        
        time = self.generator.estimate_quiz_time(10, ["true_false"])
        self.assertIn("minutes", time)
        
        time = self.generator.estimate_quiz_time(3, ["short_answer"])
        self.assertIn("minutes", time)
        
        time = self.generator.estimate_quiz_time(1, ["fill_blank"])
        self.assertIn("minutes", time)

def run_tests():
    """Run all tests"""
    print("Running quiz generator tests...\n")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestQuizGenerator)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print("\nSUCCESS: All quiz generator tests passed!")
        return True
    else:
        print("\nFAIL: Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
