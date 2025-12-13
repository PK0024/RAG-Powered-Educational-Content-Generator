# Step-by-Step Setup Guide

## ✅ What You've Done So Far
- ✅ Created project structure
- ✅ Installed dependencies
- ✅ Set up code files

## 📋 What You Need to Do Next

### Step 1: Create .env Files

You need to create 2 files with your API keys:

#### A. Backend .env File

1. Go to: `backend` folder
2. Create a new file named: `.env` (exactly this name, with the dot at the start)
3. Copy and paste this content:

```
OPENAI_API_KEY=your_openai_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=rag-educational-content
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
LOG_LEVEL=INFO
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7
```

4. Replace `your_openai_api_key_here` with your actual OpenAI API key
5. Replace `your_pinecone_api_key_here` with your actual Pinecone API key
6. Save the file

#### B. Frontend .env File

1. Go to: `frontend` folder
2. Create a new file named: `.env` (exactly this name)
3. Copy and paste this content:

```
BACKEND_API_URL=http://localhost:8000
```

4. Save the file

---

### Step 2: Start the Backend Server

1. Open PowerShell (or Command Prompt)
2. Navigate to the backend folder:
   ```powershell
   cd "C:\Users\Linata04\Desktop\Semester 4\RAG-Powered Educational Content Generator\backend"
   ```
3. Run this command:
   ```powershell
   python -m uvicorn rag_edu_generator.main:app --reload --host 0.0.0.0 --port 8000
   ```

**What you should see:**
- "Creating Pinecone index: rag-educational-content" (first time only)
- "Pinecone vector store initialized successfully"
- "Application startup complete"
- "Uvicorn running on http://0.0.0.0:8000"

**Keep this terminal window open!** The backend must keep running.

---

### Step 3: Start the Frontend (New Terminal)

1. Open a **NEW** PowerShell window (don't close the backend one!)
2. Navigate to the frontend folder:
   ```powershell
   cd "C:\Users\Linata04\Desktop\Semester 4\RAG-Powered Educational Content Generator\frontend"
   ```
3. Run this command:
   ```powershell
   streamlit run src/streamlit_app/main.py
   ```

**What will happen:**
- Streamlit will start
- Your web browser will open automatically
- You'll see the app at: `http://localhost:8501`

---

### Step 4: Use the Application

1. **Upload PDF(s):**
   - Click "Upload PDF" in the sidebar
   - Option to continue with existing document (saves credits)
   - OR Select one or multiple PDF files (up to 300 pages total)
   - Click "Upload and Index"
   - Wait for it to process
   - Filename(s) will be displayed

2. **Chat with Material:**
   - Click "Chat" in the sidebar
   - Ask questions about your PDF
   - See intelligent RAG responses with systematic prompting
   - Fallback to general knowledge if information not in document

3. **Generate Content:**
   - **Quiz**: Generate contextual quizzes with hints and detailed analytics
   - **Competitive Quiz**: Experience adaptive difficulty quizzes with Q-Learning
   - **Summary**: Get summaries of varying lengths
   - **Flashcards**: Create study flashcards

---

## ❌ Troubleshooting

### Error: "Module not found"
**Solution:** Make sure you installed all dependencies. Run:
```powershell
cd backend
pip install fastapi uvicorn[standard] llama-index llama-index-vector-stores-pinecone llama-index-embeddings-openai llama-index-llms-openai pymupdf pinecone-client pydantic pydantic-settings python-multipart python-dotenv
```

### Error: "Pinecone connection failed"
**Solution:** 
- Check your `backend/.env` file has the correct API keys
- Make sure you deleted the old Pinecone index (so it can create a new one)

### Error: "Backend connection failed" in Streamlit
**Solution:** 
- Make sure the backend is running (Step 2)
- Check that backend is on port 8000
- Verify `frontend/.env` has: `BACKEND_API_URL=http://localhost:8000`

### Port already in use
**Solution:** 
- Close other applications using ports 8000 or 8501
- Or change the port in `.env` files

---

## 📝 Quick Checklist

Before starting:
- [ ] Created `backend/.env` with API keys
- [ ] Created `frontend/.env` with backend URL
- [ ] Deleted old Pinecone index (if it existed)
- [ ] All dependencies installed

To run:
- [ ] Backend server running (Terminal 1)
- [ ] Frontend server running (Terminal 2)
- [ ] Browser opened with the app

---

## 🆘 Need Help?

If you see any errors, copy the error message and let me know!

