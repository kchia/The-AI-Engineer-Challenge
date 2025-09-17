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
        print(f"DEBUG: split_text_into_chunks called with text length: {len(text)}")
        print(f"DEBUG: AIMAKERSPACE_AVAILABLE: {AIMAKERSPACE_AVAILABLE}")
        
        if not text or not text.strip():
            print("DEBUG: No text to chunk")
            return []
            
        if not AIMAKERSPACE_AVAILABLE:
            # Simple text splitting without aimakerspace
            words = text.split()
            print(f"DEBUG: Split into {len(words)} words")
            chunks = []
            current_chunk = []
            current_size = 0
            
            for i, word in enumerate(words):
                if current_size + len(word) + 1 > chunk_size and current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    if chunk_text.strip():  # Only add non-empty chunks
                        chunks.append(chunk_text)
                        print(f"DEBUG: Added chunk {len(chunks)} with {len(chunk_text)} chars")
                    # Start new chunk with overlap
                    overlap_words = current_chunk[-chunk_overlap//10:] if len(current_chunk) > chunk_overlap//10 else current_chunk
                    current_chunk = overlap_words + [word]
                    current_size = len(' '.join(current_chunk))
                else:
                    current_chunk.append(word)
                    current_size += len(word) + 1
                
                if i < 10:  # Debug first 10 words
                    print(f"DEBUG: Word {i}: '{word}' (current_size: {current_size})")
            
            if current_chunk:
                chunk_text = ' '.join(current_chunk)
                if chunk_text.strip():  # Only add non-empty chunks
                    chunks.append(chunk_text)
                    print(f"DEBUG: Added final chunk {len(chunks)} with {len(chunk_text)} chars")
            
            print(f"DEBUG: Total chunks created: {len(chunks)}")
            return chunks
        else:
            # Use aimakerspace for better chunking
            print("DEBUG: Using aimakerspace CharacterTextSplitter")
            try:
                splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
                raw_chunks = splitter.split([text])
                print(f"DEBUG: CharacterTextSplitter returned {len(raw_chunks)} raw chunks")
                
                # Debug each raw chunk
                for i, chunk in enumerate(raw_chunks):
                    print(f"DEBUG: Raw chunk {i}: type={type(chunk)}, len={len(str(chunk)) if chunk else 0}")
                    print(f"DEBUG: Raw chunk {i} content: '{str(chunk)[:100]}...'")
                    print(f"DEBUG: Raw chunk {i} is string: {isinstance(chunk, str)}")
                    print(f"DEBUG: Raw chunk {i} has content: {bool(chunk and str(chunk).strip())}")
                
                # Filter out empty chunks and ensure they are strings
                filtered_chunks = []
                for i, chunk in enumerate(raw_chunks):
                    chunk_str = str(chunk) if chunk is not None else ""
                    if chunk_str.strip():
                        filtered_chunks.append(chunk_str)
                        print(f"DEBUG: Added chunk {i} to filtered chunks")
                    else:
                        print(f"DEBUG: Skipped chunk {i} (empty or whitespace)")
                
                print(f"DEBUG: After filtering: {len(filtered_chunks)} chunks")
                if filtered_chunks:
                    print(f"DEBUG: First filtered chunk: {filtered_chunks[0][:200]}")
                return filtered_chunks
            except Exception as e:
                print(f"DEBUG: CharacterTextSplitter failed: {e}")
                print("DEBUG: Falling back to simple chunking")
                # Fallback to simple chunking
                words = text.split()
                chunks = []
                current_chunk = []
                current_size = 0
                
                for word in words:
                    if current_size + len(word) + 1 > chunk_size and current_chunk:
                        chunk_text = ' '.join(current_chunk)
                        if chunk_text.strip():
                            chunks.append(chunk_text)
                        current_chunk = [word]
                        current_size = len(word)
                    else:
                        current_chunk.append(word)
                        current_size += len(word) + 1
                
                if current_chunk:
                    chunk_text = ' '.join(current_chunk)
                    if chunk_text.strip():
                        chunks.append(chunk_text)
                
                print(f"DEBUG: Fallback created {len(chunks)} chunks")
                return chunks
    
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
            print(f"DEBUG: Extracting text from {filename}")
            text_content = self.extract_text(tmp_file_path, filename)
            print(f"DEBUG: Extracted text length: {len(text_content) if text_content else 0}")
            print(f"DEBUG: Text preview: {text_content[:200] if text_content else 'No text'}")
            
            # Split into chunks
            print(f"DEBUG: Splitting text into chunks")
            chunks = self.split_text_into_chunks(text_content)
            print(f"DEBUG: Created {len(chunks)} chunks")
            if chunks:
                print(f"DEBUG: First chunk preview: {chunks[0][:200]}")
            
            return text_content, chunks
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_file_path)
            except:
                pass

# Create global instance
file_processor = FileProcessor()
