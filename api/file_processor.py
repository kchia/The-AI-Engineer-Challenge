#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File processing utility for educational content
Handles text extraction from various file types
"""

import os
import tempfile
from typing import List, Optional, Tuple
from fastapi import HTTPException

# Import aimakerspace modules if available
try:
    from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
    AIMAKERSPACE_AVAILABLE = True
except ImportError:
    AIMAKERSPACE_AVAILABLE = False

class FileProcessor:
    """Handles text extraction and processing from various file types"""
    
    def __init__(self):
        self.supported_extensions = {'.pdf', '.txt', '.docx', '.md'}
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
    
    def is_supported_file(self, filename: str) -> bool:
        """Check if file type is supported"""
        if not filename:
            return False
        ext = os.path.splitext(filename.lower())[1]
        return ext in self.supported_extensions
    
    def get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        if not filename:
            return ""
        return os.path.splitext(filename.lower())[1]
    
    def validate_file_size(self, content: bytes) -> None:
        """Validate file size is within limits"""
        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
            )
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        if not AIMAKERSPACE_AVAILABLE:
            raise HTTPException(
                status_code=503, 
                detail="PDF processing requires aimakerspace modules"
            )
        
        try:
            pdf_loader = PDFLoader(file_path)
            pdf_loader.load_file()
            
            if not pdf_loader.documents:
                raise ValueError("No content extracted from PDF")
            
            return pdf_loader.documents[0]
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing PDF: {str(e)}"
            )
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                raise ValueError("No content extracted from text file")
            
            return content
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                return content
            except Exception as e:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error reading text file: {str(e)}"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing text file: {str(e)}"
            )
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        try:
            from docx import Document
            doc = Document(file_path)
            content = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            
            if not content.strip():
                raise ValueError("No content extracted from DOCX file")
            
            return content
        except ImportError:
            raise HTTPException(
                status_code=500, 
                detail="DOCX processing requires python-docx package"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing DOCX file: {str(e)}"
            )
    
    def extract_text_from_md(self, file_path: str) -> str:
        """Extract text from Markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                raise ValueError("No content extracted from markdown file")
            
            return content
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error processing markdown file: {str(e)}"
            )
    
    def extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from file based on its type"""
        if not self.is_supported_file(filename):
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Supported: {', '.join(self.supported_extensions)}"
            )
        
        ext = self.get_file_extension(filename)
        
        if ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext == '.txt':
            return self.extract_text_from_txt(file_path)
        elif ext == '.docx':
            return self.extract_text_from_docx(file_path)
        elif ext == '.md':
            return self.extract_text_from_md(file_path)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {ext}"
            )
    
    def split_text_into_chunks(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split text into chunks for vector database"""
        if not text or not text.strip():
            return []
            
        if not AIMAKERSPACE_AVAILABLE:
            # Simple text splitting without aimakerspace
            words = text.split()
            chunks = []
            current_chunk = []
            current_size = 0
            
            for word in words:
                if current_size + len(word) + 1 > chunk_size and current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    if chunk_text.strip():  # Only add non-empty chunks
                        chunks.append(chunk_text)
                    # Start new chunk with overlap
                    overlap_words = current_chunk[-chunk_overlap//10:] if len(current_chunk) > chunk_overlap//10 else current_chunk
                    current_chunk = overlap_words + [word]
                    current_size = len(' '.join(current_chunk))
                else:
                    current_chunk.append(word)
                    current_size += len(word) + 1
            
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                if chunk_text.strip():  # Only add non-empty chunks
                    chunks.append(chunk_text)
            
            return chunks
        else:
            # Use aimakerspace for better chunking
            splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
            raw_chunks = splitter.split([text])
            # Filter out empty chunks and ensure they are strings
            return [chunk for chunk in raw_chunks if chunk and isinstance(chunk, str) and chunk.strip()]
    
    def process_file(self, file_content: bytes, filename: str) -> Tuple[str, List[str]]:
        """Process uploaded file and return text content and chunks"""
        # Validate file size
        self.validate_file_size(file_content)
        
        # Create temporary file
        ext = self.get_file_extension(filename)
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name
        
        try:
            # Extract text
            text_content = self.extract_text(tmp_file_path, filename)
            
            # Split into chunks
            chunks = self.split_text_into_chunks(text_content)
            
            return text_content, chunks
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_file_path)
            except:
                pass

# Create global instance
file_processor = FileProcessor()
