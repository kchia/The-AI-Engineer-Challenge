# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
import tempfile
import sys
from typing import Optional

# Add the current directory to Python path to find aimakerspace modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import aimakerspace modules (now included in the project)
try:
    from aimakerspace.text_utils import PDFLoader, CharacterTextSplitter
    from aimakerspace.vectordatabase import VectorDatabase
    AIMAKERSPACE_AVAILABLE = True
    print("aimakerspace modules loaded successfully")
except ImportError as e:
    # Fallback for deployment when aimakerspace is not available
    AIMAKERSPACE_AVAILABLE = False
    print("Warning: aimakerspace modules not available: {}. PDF features will be disabled.".format(e))
except Exception as e:
    # Catch any other errors during import
    AIMAKERSPACE_AVAILABLE = False
    print("Warning: aimakerspace modules failed to load: {}. PDF features will be disabled.".format(e))

# Import our file processor, subject categorizer, and quiz generator
from file_processor import file_processor
from subject_categorizer import subject_categorizer
from quiz_generator import create_quiz_generator

# Initialize FastAPI application with a title
app = FastAPI(title="OpenAI Chat API")

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Global variables for document context
pdf_context = None
pdf_filename = None

# Supported file types for educational content
SUPPORTED_FILE_TYPES = {
    '.pdf': 'PDF Document',
    '.txt': 'Text Document', 
    '.docx': 'Word Document',
    '.md': 'Markdown Document'
}

def get_file_type(filename: str) -> str:
    """Get file type from filename extension"""
    if not filename:
        return None
    ext = os.path.splitext(filename.lower())[1]
    return SUPPORTED_FILE_TYPES.get(ext, None)

def is_supported_file_type(filename: str) -> bool:
    """Check if file type is supported"""
    return get_file_type(filename) is not None

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    developer_message: str  # Message from the developer/system
    user_message: str  # Message from the user
    model: Optional[str] = "gpt-4.1-mini"  # Optional model selection with default
    api_key: str  # OpenAI API key for authentication

# Preprocessing function to handle incomplete prompts
def preprocess_user_message(user_message: str) -> str:
    """Enhance incomplete prompts to handle meta-testing scenarios"""
    
    # Debug logging (can be removed in production)
    # print(f"DEBUG: Original user message: '{user_message}'")
    # print(f"DEBUG: Contains 'read the following paragraph': {'read the following paragraph' in user_message.lower()}")
    # print(f"DEBUG: Contains ellipsis: {'...' in user_message or '…' in user_message}")
    
    # Check for incomplete summarization requests
    if "read the following paragraph" in user_message.lower() and ("..." in user_message or "…" in user_message):
        user_message += "\n\n[Note: No paragraph was provided in your request, so I'll use a sample paragraph to demonstrate the summarization capability. Here's the sample: 'The rapid advancement of artificial intelligence has transformed many industries. Companies are adopting AI tools to improve efficiency and reduce costs. However, this shift also raises concerns about job displacement and the need for workforce retraining.' Please summarize this sample paragraph and mention that you're using a sample since no paragraph was provided.]"
        print("DEBUG: Applied summarization enhancement")
    
    # Check for incomplete rewrite requests
    elif "rewrite the following" in user_message.lower() and ("..." in user_message or "…" in user_message):
        user_message += "\n\n[Note: No text was provided in your request, so I'll use a sample text to demonstrate the rewrite capability. Here's the sample: 'Hey guys, just wanted to let you know that the meeting is moved to next week. Can everyone make it?' Please rewrite this sample text in the requested tone.]"
        print("DEBUG: Applied rewrite enhancement")
    
    # Check for other incomplete patterns (both three dots and ellipsis character)
    elif user_message.strip().endswith("...") or user_message.strip().endswith("…"):
        user_message += "\n\n[Note: Your request seems incomplete. Please provide more details or specific content you'd like me to work with.]"
        print("DEBUG: Applied general incomplete prompt enhancement")
    
    print(f"DEBUG: Processed user message: '{user_message}'")  # Debug logging
    return user_message

# Helper function to get PDF context
def get_pdf_context(query: str, k: int = 3):
    """Get relevant context from PDF if available"""
    global pdf_context
    if not pdf_context:
        return []
    
    try:
        # Check if pdf_context is a VectorDatabase object
        if hasattr(pdf_context, 'search_by_text'):
            relevant_chunks = pdf_context.search_by_text(query, k=k, return_as_text=True)
            return relevant_chunks
        # Fallback for dictionary format
        elif isinstance(pdf_context, dict) and 'chunks' in pdf_context:
            # Simple text search in chunks for fallback mode
            chunks = pdf_context['chunks']
            query_lower = query.lower()
            relevant_chunks = []
            
            for chunk in chunks:
                if query_lower in chunk.lower():
                    relevant_chunks.append(chunk)
                    if len(relevant_chunks) >= k:
                        break
            
            # If no exact matches, return first few chunks
            if not relevant_chunks and chunks:
                relevant_chunks = chunks[:k]
            
            return relevant_chunks
        else:
            print(f"Unknown pdf_context type: {type(pdf_context)}")
            return []
    except Exception as e:
        print(f"Error retrieving PDF context: {e}")
        return []

# Enhanced developer message
def get_enhanced_developer_message(original_developer_message: str) -> str:
    """Add instructions for handling incomplete prompts"""
    
    enhancement = """
When you receive requests that seem incomplete or end with "..." :
1. If asked to summarize without provided text, create a sample paragraph and demonstrate summarization
2. If asked to rewrite without provided text, create a sample text and demonstrate the rewrite
3. Always attempt to fulfill the intent of the request by demonstrating the capability

Be helpful and proactive in demonstrating your capabilities.
"""
    
    # If there's already a developer message, append to it
    if original_developer_message.strip():
        return original_developer_message + "\n\n" + enhancement
    else:
        return enhancement

# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Initialize OpenAI client with the provided API key
        client = OpenAI(api_key=request.api_key)
        
        # Get PDF context if available
        pdf_chunks = get_pdf_context(request.user_message)
        print(f"DEBUG: PDF chunks retrieved: {len(pdf_chunks) if pdf_chunks else 0}")
        print(f"DEBUG: PDF filename: {pdf_filename}")
        if pdf_chunks:
            print(f"DEBUG: First chunk preview: {pdf_chunks[0][:200]}...")
        
        # Modify developer message to include PDF context
        enhanced_developer_message = request.developer_message
        if pdf_chunks and pdf_filename:
            context = "\n\n".join(pdf_chunks)
            enhanced_developer_message += f"\n\nUse this PDF context to answer questions about '{pdf_filename}':\n{context}"
            print(f"DEBUG: Added PDF context to developer message (length: {len(context)})")
        else:
            print("DEBUG: No PDF context available")
        
        # Preprocess messages
        enhanced_developer_message = get_enhanced_developer_message(enhanced_developer_message)
        processed_user_message = preprocess_user_message(request.user_message)
        
        # Create an async generator function for streaming responses
        async def generate():
            # Create a streaming chat completion request
            stream = client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "developer", "content": enhanced_developer_message},
                    {"role": "user", "content": processed_user_message}
                ],
                stream=True,  # Enable streaming response
                temperature=0.7,  # Reduced for more consistent responses
                max_tokens=1000,  # Ensure complete responses
            )
            
            # Yield each chunk of the response as it becomes available
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        # Return a streaming response to the client
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))

# Document upload endpoint (supports multiple file types)
@app.post("/api/upload-document")
async def upload_document(api_key: str = Form(...), file: UploadFile = File(...)):
    """Upload and process educational documents (PDF, TXT, DOCX, MD)"""
    global pdf_context, pdf_filename
    
    try:
        # Read file content
        content = await file.read()
        
        # Process file using our file processor
        text_content, chunks = file_processor.process_file(content, file.filename)
        
        # Categorize the content
        category_analysis = subject_categorizer.analyze_content(text_content)
        
        # Create vector database
        global pdf_context
        if AIMAKERSPACE_AVAILABLE:
            # Filter out empty chunks and ensure they are strings
            valid_chunks = [chunk for chunk in chunks if chunk and isinstance(chunk, str) and chunk.strip()]
            if valid_chunks:
                pdf_context = VectorDatabase(api_key=api_key)
                await pdf_context.abuild_from_list(valid_chunks)
            else:
                # Fallback if no valid chunks
                pdf_context = {"chunks": chunks, "text": text_content}
        else:
            # Fallback: store chunks in memory for basic functionality
            pdf_context = {"chunks": chunks, "text": text_content}
        
        global pdf_filename
        pdf_filename = file.filename
        file_type = get_file_type(file.filename)
        
        return {
            "success": True, 
            "filename": pdf_filename, 
            "file_type": file_type,
            "chunks": len(chunks),
            "text_length": len(text_content),
            "text_content": text_content,  # Include the actual text content
            "subject_category": category_analysis["category"],
            "category_confidence": category_analysis["confidence"],
            "category_scores": category_analysis["scores"]
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing file: {}".format(str(e)))

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

# Get supported file types for educational content
@app.get("/api/supported-file-types")
async def get_supported_file_types():
    """Get list of supported file types for educational content"""
    return {
        "supported_types": SUPPORTED_FILE_TYPES,
        "extensions": list(SUPPORTED_FILE_TYPES.keys())
    }

# Subject categorization endpoint
@app.post("/api/categorize-content")
async def categorize_content(request: dict):
    """
    Categorize educational content by subject area
    
    Request body should contain:
    - text: The text content to categorize
    - confidence_threshold: Optional confidence threshold (default: 0.1)
    """
    try:
        text = request.get("text", "")
        confidence_threshold = request.get("confidence_threshold", 0.1)
        
        if not text or not text.strip():
            return {
                "category": "Other",
                "confidence": 0.0,
                "error": "No text content provided"
            }
        
        # Categorize the content
        analysis = subject_categorizer.analyze_content(text)
        
        return {
            "success": True,
            "category": analysis["category"],
            "confidence": analysis["confidence"],
            "scores": analysis["scores"],
            "keywords_found": analysis["keywords_found"],
            "total_keywords": analysis["total_keywords"],
            "text_length": analysis["text_length"],
            "available_categories": analysis["available_categories"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error categorizing content: {}".format(str(e)))

# Get available subject categories
@app.get("/api/subject-categories")
async def get_subject_categories():
    """Get list of available subject categories"""
    return {
        "categories": subject_categorizer.get_all_categories(),
        "total_categories": len(subject_categorizer.get_all_categories())
    }

# Quiz generation endpoint
@app.post("/api/generate-quiz")
async def generate_quiz(request: dict):
    """
    Generate a quiz from educational content
    
    Request body should contain:
    - content: The educational content to generate quiz from
    - api_key: OpenAI API key
    - num_questions: Number of questions (1-10, default: 5)
    - question_types: List of question types (optional)
    """
    try:
        content = request.get("content", "")
        api_key = request.get("api_key", "")
        num_questions = request.get("num_questions", 5)
        question_types = request.get("question_types", ["multiple_choice", "true_false"])
        
        if not content or not content.strip():
            return {
                "success": False,
                "error": "No content provided"
            }
        
        if not api_key:
            return {
                "success": False,
                "error": "OpenAI API key required"
            }
        
        # Create quiz generator and generate quiz
        quiz_generator = create_quiz_generator(api_key)
        quiz_data = quiz_generator.generate_quiz(content, num_questions, question_types)
        
        return {
            "success": True,
            "quiz": quiz_data
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating quiz: {}".format(str(e)))

# Study guide generation endpoint
@app.post("/api/generate-study-guide")
async def generate_study_guide(request: dict):
    """
    Generate a study guide from educational content
    
    Request body should contain:
    - content: The educational content
    - api_key: OpenAI API key
    - subject_category: Optional subject category for context
    """
    try:
        content = request.get("content", "")
        api_key = request.get("api_key", "")
        subject_category = request.get("subject_category", None)
        
        if not content or not content.strip():
            return {
                "success": False,
                "error": "No content provided"
            }
        
        if not api_key:
            return {
                "success": False,
                "error": "OpenAI API key required"
            }
        
        # Create quiz generator and generate study guide
        quiz_generator = create_quiz_generator(api_key)
        guide_data = quiz_generator.generate_study_guide(content, subject_category)
        
        return {
            "success": True,
            "study_guide": guide_data
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error generating study guide: {}".format(str(e)))

# Get available question types
@app.get("/api/quiz-question-types")
async def get_question_types():
    """Get list of available question types for quiz generation"""
    return {
        "question_types": ["multiple_choice", "true_false", "short_answer", "fill_blank"],
        "descriptions": {
            "multiple_choice": "Multiple choice questions with 4 options",
            "true_false": "True or false questions",
            "short_answer": "Short answer questions requiring brief responses",
            "fill_blank": "Fill in the blank questions"
        }
    }

# Debug endpoint to check aimakerspace availability
@app.get("/api/debug/aimakerspace")
async def debug_aimakerspace():
    """Debug endpoint to check aimakerspace module availability"""
    import sys
    import os

    debug_info = {
        "aimakerspace_available": AIMAKERSPACE_AVAILABLE,
        "python_version": sys.version,
        "python_path": sys.path,
        "current_directory": os.getcwd(),
        "api_directory_contents": []
    }

    try:
        api_dir = os.path.dirname(os.path.abspath(__file__))
        debug_info["api_directory_contents"] = os.listdir(api_dir)

        aimakerspace_dir = os.path.join(api_dir, "aimakerspace")
        if os.path.exists(aimakerspace_dir):
            debug_info["aimakerspace_directory_contents"] = os.listdir(aimakerspace_dir)
        else:
            debug_info["aimakerspace_directory_exists"] = False
    except Exception as e:
        debug_info["directory_scan_error"] = str(e)

    # Try individual imports
    import_results = {}
    try:
        import aimakerspace
        import_results["aimakerspace_base"] = "success"
    except Exception as e:
        import_results["aimakerspace_base"] = str(e)

    try:
        from aimakerspace.text_utils import PDFLoader
        import_results["pdf_loader"] = "success"
    except Exception as e:
        import_results["pdf_loader"] = str(e)

    try:
        from aimakerspace.vectordatabase import VectorDatabase
        import_results["vector_database"] = "success"
    except Exception as e:
        import_results["vector_database"] = str(e)

    try:
        from aimakerspace.openai_utils.embedding import EmbeddingModel
        import_results["embedding_model"] = "success"
    except Exception as e:
        import_results["embedding_model"] = str(e)

    debug_info["import_results"] = import_results

    return debug_info

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
