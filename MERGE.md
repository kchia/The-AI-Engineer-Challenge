# Simple PDF RAG Integration - Merge Instructions

This feature branch adds simple PDF upload and RAG (Retrieval-Augmented Generation) functionality to the AI Chat application using the `aimakerspace` library.

## Changes Made

### Backend Changes

- **Updated `api/requirements.txt`**: Added PyPDF2, numpy, and python-dotenv dependencies
- **Updated `api/app.py`**:
  - Added PDF upload endpoint (`/api/upload-pdf`)
  - Modified existing chat endpoint to use PDF context when available
  - Added simple PDF context retrieval using aimakerspace library

### Frontend Changes

- **Updated `frontend/components/ChatInterface.tsx`**:
  - Added simple PDF file upload in settings panel
  - Added PDF status display in header
  - Updated welcome message to reflect PDF mode

## New Features

1. **PDF Upload**: Users can upload PDF files through the settings panel
2. **Automatic RAG**: PDF content is automatically used as context when available
3. **Simple UI**: Clean, minimal interface without complex state management

## How It Works

1. User uploads a PDF through the settings panel
2. PDF is processed and indexed using aimakerspace library
3. When user asks questions, relevant PDF content is automatically retrieved and used as context
4. LLM responds using only the PDF content when available

## Merge Instructions

### Option 1: GitHub Web Interface (Recommended)

1. Go to the repository on GitHub
2. Click "Pull requests" tab
3. Click "New pull request"
4. Select `feature/simple-pdf-rag` as the source branch and `main` as the target branch
5. Add title: "Add Simple PDF Upload and RAG Functionality"
6. Review and merge

### Option 2: GitHub CLI

```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Merge the feature branch
git merge feature/simple-pdf-rag

# Push to remote
git push origin main

# Delete the feature branch (optional)
git branch -d feature/simple-pdf-rag
git push origin --delete feature/simple-pdf-rag
```

## Testing Before Merge

1. Install dependencies:

   ```bash
   cd api
   pip install -r requirements.txt
   ```

2. Start backend:

   ```bash
   cd api
   python app.py
   ```

3. Start frontend:

   ```bash
   cd frontend
   npm run dev
   ```

4. Test PDF upload and chat functionality

## Dependencies

- Backend: PyPDF2, numpy, python-dotenv (added to requirements.txt)
- External: aimakerspace library (must be available at specified path)

## Notes

- Simple implementation without overengineering
- PDF context is automatically used when available
- No complex state management or mode switching
- Clean, minimal user interface
