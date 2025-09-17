#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quiz generation utility for educational content
Uses GPT to generate quizzes from educational materials
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from openai import OpenAI

class QuizGenerator:
    """Generates quizzes from educational content using GPT"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.question_types = ["multiple_choice", "true_false", "short_answer", "fill_blank"]
    
    def generate_quiz_prompt(self, content: str, num_questions: int = 5, question_types: List[str] = None) -> str:
        """Generate prompt for quiz generation"""
        if question_types is None:
            question_types = ["multiple_choice", "true_false"]
        
        prompt = f"""
You are an expert educational quiz generator. Generate a quiz based on the following educational content.

Content:
{content[:2000]}  # Limit content to avoid token limits

Requirements:
- Generate exactly {num_questions} questions
- Use these question types: {', '.join(question_types)}
- Questions should test understanding, not just memorization
- Include a mix of difficulty levels (easy, medium, hard)
- Make questions clear and unambiguous
- Provide correct answers and explanations

Format your response as a JSON object with this structure:
{{
    "title": "Quiz Title",
    "description": "Brief description of the quiz",
    "questions": [
        {{
            "id": 1,
            "type": "multiple_choice",
            "question": "What is the main topic?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "explanation": "Explanation of why this is correct",
            "difficulty": "easy"
        }},
        {{
            "id": 2,
            "type": "true_false",
            "question": "This statement is true or false?",
            "correct_answer": true,
            "explanation": "Explanation of the correct answer",
            "difficulty": "medium"
        }}
    ],
    "total_questions": {num_questions},
    "estimated_time": "10-15 minutes"
}}

Important:
- Return ONLY the JSON object, no additional text
- Ensure all questions are relevant to the provided content
- Make sure the JSON is valid and properly formatted
- Include explanations for all answers
"""
        return prompt
    
    def generate_quiz(self, content: str, num_questions: int = 5, question_types: List[str] = None) -> Dict:
        """
        Generate a quiz from educational content
        
        Args:
            content: The educational content to generate quiz from
            num_questions: Number of questions to generate (1-10)
            question_types: List of question types to include
            
        Returns:
            Dictionary containing the generated quiz
        """
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        if num_questions < 1 or num_questions > 10:
            raise ValueError("Number of questions must be between 1 and 10")
        
        if question_types is None:
            question_types = ["multiple_choice", "true_false"]
        
        # Validate question types
        for qtype in question_types:
            if qtype not in self.question_types:
                raise ValueError(f"Invalid question type: {qtype}")
        
        try:
            # Generate the prompt
            prompt = self.generate_quiz_prompt(content, num_questions, question_types)
            
            # Call GPT to generate the quiz
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educational quiz generator. Generate high-quality quizzes based on educational content."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract the response
            quiz_text = response.choices[0].message.content.strip()
            
            # Try to parse as JSON
            try:
                quiz_data = json.loads(quiz_text)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from the response
                json_match = re.search(r'\{.*\}', quiz_text, re.DOTALL)
                if json_match:
                    quiz_data = json.loads(json_match.group())
                else:
                    raise ValueError("Failed to parse quiz as JSON")
            
            # Validate the quiz structure
            self._validate_quiz_structure(quiz_data, num_questions)
            
            return quiz_data
            
        except Exception as e:
            raise Exception(f"Error generating quiz: {str(e)}")
    
    def _validate_quiz_structure(self, quiz_data: Dict, expected_questions: int) -> None:
        """Validate the structure of the generated quiz"""
        required_fields = ["title", "description", "questions", "total_questions"]
        
        for field in required_fields:
            if field not in quiz_data:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(quiz_data["questions"], list):
            raise ValueError("Questions must be a list")
        
        if len(quiz_data["questions"]) != expected_questions:
            raise ValueError(f"Expected {expected_questions} questions, got {len(quiz_data['questions'])}")
        
        # Validate each question
        for i, question in enumerate(quiz_data["questions"]):
            self._validate_question(question, i + 1)
    
    def _validate_question(self, question: Dict, question_num: int) -> None:
        """Validate a single question"""
        required_fields = ["id", "type", "question", "correct_answer", "explanation", "difficulty"]
        
        for field in required_fields:
            if field not in question:
                raise ValueError(f"Question {question_num} missing required field: {field}")
        
        # Validate question type
        if question["type"] not in self.question_types:
            raise ValueError(f"Question {question_num} has invalid type: {question['type']}")
        
        # Validate question content
        if not question["question"] or len(question["question"].strip()) < 10:
            raise ValueError(f"Question {question_num} is too short or empty")
        
        # Validate based on question type
        if question["type"] == "multiple_choice":
            if "options" not in question or not isinstance(question["options"], list):
                raise ValueError(f"Question {question_num} (multiple choice) missing options")
            if len(question["options"]) < 2:
                raise ValueError(f"Question {question_num} (multiple choice) needs at least 2 options")
            if question["correct_answer"] not in question["options"]:
                raise ValueError(f"Question {question_num} correct answer not in options")
        
        elif question["type"] == "true_false":
            if not isinstance(question["correct_answer"], bool):
                raise ValueError(f"Question {question_num} (true/false) correct answer must be boolean")
        
        # Validate difficulty
        valid_difficulties = ["easy", "medium", "hard"]
        if question["difficulty"] not in valid_difficulties:
            raise ValueError(f"Question {question_num} has invalid difficulty: {question['difficulty']}")
    
    def generate_study_guide(self, content: str, subject_category: str = None) -> Dict:
        """
        Generate a study guide from educational content
        
        Args:
            content: The educational content
            subject_category: Optional subject category for context
            
        Returns:
            Dictionary containing the study guide
        """
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        try:
            # Create study guide prompt
            subject_context = f" (Subject: {subject_category})" if subject_category else ""
            prompt = f"""
Create a comprehensive study guide based on the following educational content{subject_context}:

Content:
{content[:2000]}

Format your response as a JSON object with this structure:
{{
    "title": "Study Guide Title",
    "subject": "{subject_category or 'General'}",
    "key_concepts": [
        "Concept 1: Brief explanation",
        "Concept 2: Brief explanation"
    ],
    "important_points": [
        "Important point 1",
        "Important point 2"
    ],
    "study_tips": [
        "Study tip 1",
        "Study tip 2"
    ],
    "practice_questions": [
        "Practice question 1",
        "Practice question 2"
    ],
    "summary": "Brief summary of the main topics",
    "estimated_study_time": "30-45 minutes"
}}

Important:
- Return ONLY the JSON object, no additional text
- Make it comprehensive but concise
- Focus on the most important concepts
- Include practical study advice
- Ensure the JSON is valid and properly formatted
"""
            
            # Call GPT to generate the study guide
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator. Create comprehensive study guides from educational materials."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            # Extract and parse the response
            guide_text = response.choices[0].message.content.strip()
            
            try:
                guide_data = json.loads(guide_text)
            except json.JSONDecodeError:
                json_match = re.search(r'\{.*\}', guide_text, re.DOTALL)
                if json_match:
                    guide_data = json.loads(json_match.group())
                else:
                    raise ValueError("Failed to parse study guide as JSON")
            
            return guide_data
            
        except Exception as e:
            raise Exception(f"Error generating study guide: {str(e)}")
    
    def get_available_question_types(self) -> List[str]:
        """Get list of available question types"""
        return self.question_types.copy()
    
    def estimate_quiz_time(self, num_questions: int, question_types: List[str]) -> str:
        """Estimate time needed to complete quiz"""
        time_per_question = {
            "multiple_choice": 1.5,
            "true_false": 0.5,
            "short_answer": 2.0,
            "fill_blank": 1.0
        }
        
        total_time = 0
        for qtype in question_types:
            total_time += time_per_question.get(qtype, 1.0)
        
        total_time *= num_questions
        
        if total_time < 5:
            return "5-10 minutes"
        elif total_time < 15:
            return "10-15 minutes"
        elif total_time < 30:
            return "15-30 minutes"
        else:
            return "30+ minutes"

# Factory function to create quiz generator
def create_quiz_generator(api_key: str) -> QuizGenerator:
    """Create a new QuizGenerator instance"""
    return QuizGenerator(api_key)
