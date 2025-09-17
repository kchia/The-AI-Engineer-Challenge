#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subject categorization utility for educational content
Uses keyword-based classification to categorize educational materials
"""

import re
from typing import Dict, List, Tuple, Optional
from collections import Counter

class SubjectCategorizer:
    """Categorizes educational content by subject area"""
    
    def __init__(self):
        # Define subject categories with their keywords
        self.categories = {
            "Mathematics": {
                "keywords": [
                    "algebra", "geometry", "calculus", "trigonometry", "statistics", "probability",
                    "equation", "formula", "theorem", "proof", "derivative", "integral", "matrix",
                    "function", "graph", "coordinate", "angle", "triangle", "circle", "square",
                    "number", "fraction", "decimal", "percentage", "ratio", "proportion",
                    "solve", "calculate", "compute", "mathematical", "arithmetic", "numerical"
                ],
                "weight": 1.0
            },
            "Science": {
                "keywords": [
                    "physics", "chemistry", "biology", "anatomy", "physiology", "genetics",
                    "molecule", "atom", "electron", "proton", "neutron", "element", "compound",
                    "reaction", "experiment", "hypothesis", "theory", "law", "principle",
                    "energy", "force", "motion", "gravity", "magnetism", "electricity",
                    "cell", "tissue", "organ", "system", "evolution", "species", "ecosystem",
                    "laboratory", "scientific", "research", "observation", "measurement"
                ],
                "weight": 1.0
            },
            "Literature": {
                "keywords": [
                    "poetry", "novel", "story", "character", "plot", "theme", "setting",
                    "author", "writer", "literature", "book", "chapter", "paragraph",
                    "metaphor", "simile", "symbolism", "imagery", "rhyme", "rhythm",
                    "narrative", "dialogue", "monologue", "prose", "verse", "stanza",
                    "analysis", "criticism", "interpretation", "meaning", "message",
                    "classic", "contemporary", "fiction", "non-fiction", "biography"
                ],
                "weight": 1.0
            },
            "History": {
                "keywords": [
                    "history", "historical", "ancient", "medieval", "modern", "century",
                    "war", "battle", "revolution", "empire", "kingdom", "civilization",
                    "culture", "society", "government", "politics", "economy", "trade",
                    "discovery", "exploration", "colonization", "independence", "freedom",
                    "timeline", "chronology", "era", "period", "age", "decade", "year",
                    "document", "artifact", "evidence", "source", "primary", "secondary"
                ],
                "weight": 1.0
            },
            "Language": {
                "keywords": [
                    "grammar", "syntax", "vocabulary", "pronunciation", "spelling",
                    "sentence", "paragraph", "essay", "composition", "writing",
                    "reading", "comprehension", "fluency", "communication", "speech",
                    "language", "linguistic", "phonetics", "morphology", "semantics",
                    "conjugation", "declension", "tense", "mood", "voice", "aspect",
                    "translation", "interpretation", "bilingual", "multilingual"
                ],
                "weight": 1.0
            },
            "Arts": {
                "keywords": [
                    "art", "painting", "drawing", "sculpture", "music", "dance", "theater",
                    "drama", "performance", "creative", "artistic", "aesthetic", "beauty",
                    "design", "color", "shape", "form", "texture", "composition",
                    "gallery", "museum", "exhibition", "masterpiece", "work", "piece",
                    "technique", "style", "movement", "period", "renaissance", "baroque"
                ],
                "weight": 1.0
            },
            "Technology": {
                "keywords": [
                    "computer", "software", "hardware", "programming", "code", "algorithm",
                    "data", "database", "network", "internet", "website", "application",
                    "digital", "electronic", "technology", "innovation", "development",
                    "system", "platform", "interface", "user", "experience", "design",
                    "artificial", "intelligence", "machine", "learning", "automation"
                ],
                "weight": 1.0
            },
            "Other": {
                "keywords": [],
                "weight": 0.1  # Default category with low weight
            }
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        processed_text = self.preprocess_text(text)
        
        if not processed_text:
            return []
        
        # Split into words and filter out common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
            "by", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "will", "would", "could", "should", "may", "might", "can",
            "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they",
            "me", "him", "her", "us", "them", "my", "your", "his", "her", "its", "our", "their"
        }
        
        words = processed_text.split()
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords
    
    def calculate_category_scores(self, keywords: List[str]) -> Dict[str, float]:
        """Calculate scores for each category based on keyword matches"""
        scores = {}
        
        for category, config in self.categories.items():
            if category == "Other":
                continue  # Skip "Other" category in scoring
            
            category_keywords = config["keywords"]
            weight = config["weight"]
            
            # Count keyword matches
            matches = 0
            for keyword in keywords:
                for cat_keyword in category_keywords:
                    if keyword in cat_keyword or cat_keyword in keyword:
                        matches += 1
                        break  # Count each keyword only once per category
            
            # Calculate score (matches * weight / total keywords)
            if keywords:
                scores[category] = (matches * weight) / len(keywords)
            else:
                scores[category] = 0.0
        
        return scores
    
    def categorize_text(self, text: str, confidence_threshold: float = 0.1) -> Tuple[str, float, Dict[str, float]]:
        """
        Categorize text content
        
        Args:
            text: Text content to categorize
            confidence_threshold: Minimum confidence score for categorization
            
        Returns:
            Tuple of (category, confidence, all_scores)
        """
        if not text or not text.strip():
            return "Other", 0.0, {}
        
        # Extract keywords
        keywords = self.extract_keywords(text)
        
        if not keywords:
            return "Other", 0.0, {}
        
        # Calculate scores for all categories
        scores = self.calculate_category_scores(keywords)
        
        # Find the category with the highest score
        if not scores:
            return "Other", 0.0, {}
        
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]
        
        # If confidence is too low, return "Other"
        if best_score < confidence_threshold:
            return "Other", best_score, scores
        
        return best_category, best_score, scores
    
    def get_category_keywords(self, category: str) -> List[str]:
        """Get keywords for a specific category"""
        return self.categories.get(category, {}).get("keywords", [])
    
    def get_all_categories(self) -> List[str]:
        """Get list of all available categories"""
        return list(self.categories.keys())
    
    def analyze_content(self, text: str) -> Dict:
        """
        Comprehensive content analysis
        
        Returns:
            Dictionary with category, confidence, scores, and metadata
        """
        category, confidence, scores = self.categorize_text(text)
        keywords = self.extract_keywords(text)
        
        return {
            "category": category,
            "confidence": confidence,
            "scores": scores,
            "keywords_found": keywords[:20],  # Top 20 keywords
            "total_keywords": len(keywords),
            "text_length": len(text),
            "available_categories": self.get_all_categories()
        }

# Create global instance
subject_categorizer = SubjectCategorizer()
