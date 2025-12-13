# RAG-Powered Educational Content Generator - Project Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features & Functionalities](#features--functionalities)
3. [Technical Architecture](#technical-architecture)
4. [User Flow](#user-flow)
5. [System Flow](#system-flow)
6. [Key Components](#key-components)
7. [Adaptive Learning System](#adaptive-learning-system)

---

## 🎯 Overview

The **RAG-Powered Educational Content Generator** is a comprehensive educational platform that allows users to upload PDF documents, extract and index their content using RAG (Retrieval-Augmented Generation), and interact with the material through various educational tools including chat, quizzes, flashcards, and summaries. The system features an innovative **adaptive competitive quiz** that uses Q-Learning and Thompson Sampling to personalize difficulty based on user performance.

### Core Technology Stack
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit (Python)
- **Vector Database**: Pinecone (with namespace isolation)
- **LLM Framework**: LlamaIndex
- **Embeddings**: OpenAI (text-embedding-3-small, 1536 dimensions)
- **LLM**: OpenAI GPT-4 Turbo
- **PDF Processing**: PyMuPDF
- **Adaptive Learning**: Q-Learning + Thompson Sampling (NumPy)

---

## ✨ Features & Functionalities

### 1. **PDF Upload & Processing**
- **Upload multiple PDF documents** (up to 300 pages total, 200MB limit per file)
- **File type validation**: Only PDF files accepted
- **Extract text content** from PDFs using PyMuPDF
- **Hybrid chunking strategy**:
  - Respects page boundaries
  - Semantic chunking within pages
  - Maintains page number metadata
  - Preserves filename information
- **Automatic indexing** to Pinecone vector database
- **Namespace isolation**: Each document gets a unique namespace (UUID) for session-based isolation
- **Document persistence**: Option to continue with previously uploaded documents
- **Real-time logging** of chunking process with previews
- **Filename preservation**: Actual filenames displayed throughout the UI

### 2. **Chat with Material (RAG Chat)**
- **Interactive Q&A** with uploaded documents
- **RAG-powered responses** grounded in document content
- **Systematic prompting strategies**:
  - Question type detection (list, definition, comparison, how, why, what, general)
  - Dynamic prompt generation based on question type
  - Educational assistant persona
  - Structured response formatting
- **Context management**:
  - Quality filtering (removes chunks < 50 characters)
  - Relevance sorting by similarity score
  - Token limit management (~4000 tokens)
  - Intelligent context window handling
- **Intelligent fallback mechanism**:
  - Dual detection system (pre-query + post-query)
  - Explicitly states when information is not in documents
  - Provides general knowledge answers when appropriate
- **Source citations** showing which parts of the document were used
- **Document-scoped queries** (isolated per document using namespaces)
- **Filename display**: Shows current document name in UI and responses
- **Special handling**: Detects questions about uploaded materials and responds directly

### 3. **Quiz Generation & Taking**
- **Mixed-format quizzes**:
  - Multiple Choice Questions (MCQ) with 4 options
  - Short Answer Questions
- **Contextual questions** with sufficient background information (self-contained)
- **Interactive quiz taking**:
  - Radio buttons for MCQ selection
  - Text areas for short answers
  - Hints available for each question (without revealing answers)
  - Questions and options persist after submission
- **AI-powered evaluation**:
  - Automatic scoring for MCQ
  - LLM-based evaluation for short answers (semantic comparison)
- **Comprehensive results**:
  - Color-coded feedback (green for correct, red for incorrect)
  - User's answer shown first (green if correct, red if incorrect)
  - Correct answer shown only when user's answer was wrong
  - Full option text displayed (not just "Option C")
  - Detailed explanations for each question
  - MCQ options remain visible for review
- **Statistical Performance Report**:
  - Key Performance Indicators (KPIs): Total correct, accuracy rate, completion rate
  - Visual charts (pie charts, bar charts, performance levels)
  - Question-by-question performance table
  - Detailed breakdown by question type
  - Personalized insights and recommendations

### 4. **Competitive Quiz (Adaptive Learning)**
- **Question Bank Generation**:
  - Generates 50 MCQ questions by default
  - Three difficulty levels: Low, Medium, Hard
  - Questions generated from uploaded material or user-specified topic
  - Each question includes a hint
  - Questions stored with difficulty metadata
- **Adaptive Difficulty System**:
  - **Q-Learning Algorithm**: Learns optimal difficulty selection based on user performance
  - **Thompson Sampling**: Bayesian approach for exploration-exploitation balance
  - Difficulty increases when user answers correctly
  - Difficulty decreases when user answers incorrectly
  - Real-time difficulty adjustment after each answer
- **Reward System**:
  - Positive rewards for correct answers (varies by difficulty: +0.50 to +1.00)
  - Negative rewards for incorrect answers (varies by difficulty: -0.50 to -0.75)
  - Reward values reflect difficulty level
- **Quiz Session**:
  - User selects 5-10 questions from the bank
  - One question displayed at a time
  - "Request Hint" button for each question
  - Submit answer → See result → Next question
  - Answer history tracking with difficulty and reward
- **Results Display**:
  - Question and options persist after submission
  - Visual indicators (green/red) for user's answer and correct answer
  - Full option text displayed
  - Reward shown for each answer
  - Final statistics: Total correct, accuracy, average reward
  - Answer history: `Q1 (medium): ❌ Reward: -0.50`
- **Session Management**:
  - Option to continue with previously generated quiz bank
  - Option to generate new quiz bank
  - Quiz state persistence

### 5. **Flashcard Generation**
- **Generate flashcards** from document content
- **Front/Back format**:
  - Front: Question or term
  - Back: Answer or definition (displayed in black for visibility)
- **Category tagging** (definition, concept, fact, etc.)
- **Interactive study**:
  - Navigate between cards
  - Show/Hide answer functionality
  - Clear visual design with color-coded answers
- **Download flashcards** as JSON

### 6. **Summary Generation**
- **Three length options**:
  - Short (2-3 paragraphs, ~150-200 words)
  - Medium (4-6 paragraphs, ~300-400 words)
  - Long (8-10 paragraphs, ~600-800 words)
- **Structured summaries** with:
  - Summary title
  - Key topics list
  - Word count
- **Comprehensive coverage** of main ideas and concepts

### 7. **Document Management**
- **List existing documents**: View previously uploaded documents in Pinecone
- **Continue with existing document**: Option to use previously uploaded document without re-uploading
- **Filename extraction**: Extracts and displays actual filenames from metadata
- **Session isolation**: Each document session is isolated using Pinecone namespaces

---

## 🏗️ Technical Architecture

### Backend Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Upload     │  │     Chat     │  │    Quiz     │  │
│  │   Route      │  │    Route     │  │   Route     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
│  ┌──────▼──────────────────▼──────────────────▼──────┐ │
│  │           Service Layer                              │ │
│  │  ┌──────────────┐  ┌──────────────┐                │ │
│  │  │   RAG        │  │   Content    │                │ │
│  │  │  Service     │  │  Generator   │                │ │
│  │  └──────┬───────┘  └──────┬───────┘                │ │
│  │         │                  │                        │ │
│  │  ┌──────▼──────────────────▼───────┐                │ │
│  │  │    Vector Store Service          │                │ │
│  │  └──────┬───────────────────────────┘                │ │
│  └─────────┼────────────────────────────────────────────┘ │
│            │                                               │
│  ┌─────────▼─────────┐  ┌──────────────┐                 │
│  │   Pinecone        │  │   OpenAI     │                 │
│  │  Vector DB        │  │   API        │                 │
│  │  (Namespaces)     │  │              │                 │
│  └───────────────────┘  └──────────────┘                 │
│                                                           │
│  ┌──────────────────────────────────────────────────────┐ │
│  │     Competitive Quiz Service                        │ │
│  │  ┌──────────────┐  ┌──────────────┐               │ │
│  │  │ Q-Learning   │  │  Thompson    │               │ │
│  │  │   Agent      │  │  Sampling    │               │ │
│  │  └──────────────┘  └──────────────┘               │ │
│  └──────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

### Frontend Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Streamlit Frontend                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Upload  │  │   Chat   │  │   Quiz   │  │Summary  │ │
│  │   Page   │  │   Page   │  │   Page   │  │  Page   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       │             │              │              │      │
│  ┌────▼─────────────▼──────────────▼──────────────▼────┐ │
│  │           API Client (HTTP Client)                  │ │
│  └───────────────────────┬────────────────────────────┘ │
│                          │                                │
│  ┌───────────────────────▼────────────────────────────┐ │
│  │         FastAPI Backend (REST API)                  │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │     Competitive Quiz Page                            │ │
│  │  - Question Bank Generation                         │ │
│  │  - Adaptive Quiz Taking                            │ │
│  │  - Real-time Statistics                            │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

---

## 🔄 User Flow

### Main User Journey

```
1. START
   │
   ├─► Navigate to Upload Page
   │   │
   │   ├─► Check for existing documents
   │   │   ├─► Continue with existing document (saves credits)
   │   │   └─► OR Upload new PDF(s)
   │   │
   │   ├─► Select PDF file(s) (up to 300 pages total)
   │   ├─► Upload PDF(s)
   │   │
   │   └─► System processes:
   │       ├─► Extract text from PDF(s)
   │       ├─► Combine multiple PDFs with separators
   │       ├─► Chunk document (hybrid strategy)
   │       ├─► Generate embeddings
   │       ├─► Store in Pinecone (with namespace)
   │       └─► Return document_id and filename(s)
   │
   │   ┌─────────────────────────────┐
   │   │ Document ID generated       │
   │   │ Filename(s) stored          │
   │   │ Document ready for use      │
   │   └─────────────────────────────┘
   │
   ├─► Choose Feature:
   │   │
   │   ├─► CHAT
   │   │   ├─► Enter question
   │   │   ├─► System detects question type
   │   │   ├─► Retrieves relevant chunks (with filtering)
   │   │   ├─► Generates dynamic prompt
   │   │   ├─► LLM generates answer
   │   │   ├─► Post-processes response
   │   │   ├─► Checks for fallback need
   │   │   └─► Display answer + sources + filename
   │   │
   │   ├─► QUIZ
   │   │   ├─► Configure quiz (number, types)
   │   │   ├─► Generate quiz questions (contextual)
   │   │   ├─► Take quiz:
   │   │   │   ├─► Answer MCQ (radio buttons)
   │   │   │   ├─► Answer short questions (text)
   │   │   │   ├─► Use hints if needed
   │   │   │   └─► View question and options
   │   │   ├─► Submit quiz
   │   │   └─► View results:
   │   │       ├─► Performance metrics
   │   │       ├─► Visual charts
   │   │       ├─► Question-by-question review
   │   │       └─► Insights & recommendations
   │   │
   │   ├─► COMPETITIVE QUIZ
   │   │   ├─► Check for existing quiz bank
   │   │   │   ├─► Continue with existing quiz
   │   │   │   └─► OR Generate new quiz bank
   │   │   │
   │   │   ├─► Generate Question Bank (50 MCQs):
   │   │   │   ├─► From uploaded material OR
   │   │   │   └─► From user-specified topic
   │   │   │
   │   │   ├─► Start Quiz (5-10 questions):
   │   │   │   ├─► First question (medium difficulty)
   │   │   │   ├─► Request hint (optional)
   │   │   │   ├─► Submit answer
   │   │   │   ├─► See result (correct/incorrect, reward)
   │   │   │   ├─► Next question (adjusted difficulty)
   │   │   │   └─► Repeat until complete
   │   │   │
   │   │   └─► View Final Results:
   │   │       ├─► Answer history with difficulty & reward
   │   │       ├─► Final statistics
   │   │       └─► Performance summary
   │   │
   │   ├─► FLASHCARDS
   │   │   ├─► Configure number of cards
   │   │   ├─► Generate flashcards
   │   │   ├─► Study cards:
   │   │   │   ├─► View front (question)
   │   │   │   ├─► Show answer (black text)
   │   │   │   └─► Navigate between cards
   │   │   └─► Download flashcards
   │   │
   │   └─► SUMMARY
   │       ├─► Select length (short/medium/long)
   │       ├─► Generate summary
   │       └─► View summary with key topics
   │
   └─► END
```

---

## 🔧 System Flow

### PDF Upload Flow (Multiple Files)

```
User uploads multiple PDFs
    │
    ▼
FastAPI receives files
    │
    ▼
Validate file types (PDF only)
    │
    ▼
Extract text from each PDF (PyMuPDF)
    │
    ▼
Combine PDFs with separators
    │
    ▼
HybridChunker processes:
    ├─► Split by pages
    ├─► Semantic chunking within pages
    └─► Add metadata (page numbers, filenames, chunk indices)
    │
    ▼
Convert to LlamaIndex Documents
    │
    ▼
Generate embeddings (OpenAI, 1536 dims)
    │
    ▼
Store in Pinecone Vector DB
    ├─► Unique namespace (UUID = document_id)
    ├─► Filename in metadata
    └─► Page numbers preserved
    │
    ▼
Return Document ID + Filenames to user
```

### Chat Flow (RAG with Systematic Prompting)

```
User asks question
    │
    ▼
Detect question type (7 categories)
    │
    ▼
Query embedded (OpenAI)
    │
    ▼
Semantic search in Pinecone (with namespace filter)
    │
    ▼
Retrieve top-k relevant chunks
    │
    ▼
Quality filtering (< 50 chars removed)
    │
    ▼
Sort by similarity score
    │
    ▼
Manage context window (token limits)
    │
    ▼
Create dynamic prompt (based on question type)
    │
    ▼
Send to LLM with:
    ├─► User question
    ├─► Retrieved context
    ├─► Type-specific instructions
    └─► Educational guidelines
    │
    ▼
LLM generates answer
    │
    ▼
Post-process answer:
    ├─► Remove redundant phrases
    ├─► Improve structure
    └─► Remove markdown artifacts
    │
    ▼
Check for fallback need:
    ├─► Check similarity scores
    └─► Check response for "no information" phrases
    │
    ▼
Return answer + sources + filename
```

### Competitive Quiz Flow (Adaptive Learning)

```
User requests competitive quiz
    │
    ▼
Generate Question Bank (50 MCQs):
    ├─► Retrieve diverse context from document OR
    └─► Use user-specified topic
    │
    ▼
LLM generates questions with:
    ├─► Three difficulty levels (low, medium, hard)
    ├─► Hints for each question
    └─► Correct answers and explanations
    │
    ▼
Store question bank (with quiz_id)
    │
    ▼
User starts quiz (5-10 questions):
    ├─► Initialize Q-Learning agent
    ├─► Initialize Thompson Sampling agent
    ├─► Start with medium difficulty
    └─► Create session
    │
    ▼
For each question:
    │
    ├─► Display question (with difficulty badge)
    ├─► User can request hint
    ├─► User submits answer
    │
    ├─► Evaluate answer:
    │   ├─► Check correctness
    │   └─► Calculate reward
    │
    ├─► Update Q-Learning:
    │   ├─► Update Q-values
    │   └─► Learn optimal difficulty selection
    │
    ├─► Thompson Sampling:
    │   ├─► Update beta distributions
    │   └─► Select next difficulty (exploration-exploitation)
    │
    ├─► Adaptive Quiz Manager:
    │   ├─► Calculate performance trend
    │   ├─► Determine next difficulty
    │   └─► Adjust based on correctness
    │
    ├─► Display result:
    │   ├─► Correct/incorrect
    │   ├─► Reward
    │   ├─► Explanation
    │   └─► Next difficulty level
    │
    └─► Select next question (matching difficulty)
    │
    ▼
Quiz complete:
    ├─► Calculate final statistics
    ├─► Display answer history
    └─► Show performance summary
```

### Quiz Evaluation Flow

```
User submits quiz
    │
    ▼
For each question:
    │
    ├─► Multiple Choice:
    │   ├─► Compare user selection with correct answer
    │   └─► Mark correct/incorrect
    │
    └─► Short Answer:
        ├─► Send to evaluation endpoint:
        │   ├─► User answer
        │   ├─► Correct answer
        │   └─► Question text
        │
        ├─► LLM evaluates:
        │   ├─► Semantic comparison
        │   ├─► Key concept matching
        │   └─► Returns is_correct + feedback
        │
        └─► Mark correct/incorrect
    │
    ▼
Calculate statistics:
    ├─► Total correct
    ├─► Accuracy rate
    ├─► Completion rate
    └─► Performance by type
    │
    ▼
Generate visualizations:
    ├─► Pie chart (correct/incorrect)
    ├─► Bar chart (by question type)
    └─► Performance level indicator
    │
    ▼
Display results + insights
```

---

## 🧩 Key Components

### Backend Components

#### 1. **Vector Store Service** (`vector_store.py`)
- Manages Pinecone connection
- Handles index creation/retrieval
- Document storage operations
- Namespace isolation support
- Filename metadata storage

#### 2. **RAG Service** (`rag_service.py`)
- Document indexing with namespace support
- Context retrieval with quality filtering
- Query processing with systematic prompting
- Question type detection
- Dynamic prompt generation
- Context window management
- Response post-processing
- Fallback mechanism
- Integration with LlamaIndex

#### 3. **Content Generator** (`content_generator.py`)
- Quiz generation (contextual questions with hints)
- Flashcard generation
- Summary generation
- Answer evaluation (LLM-based for short answers)
- Competitive quiz question bank generation

#### 4. **Competitive Quiz Service** (`competitive_quiz_service.py`)
- Question bank management
- Quiz session management
- Answer submission handling
- Integration with adaptive learning algorithms

#### 5. **Adaptive Learning** (`adaptive_learning.py`)
- **QLearningAgent**: Q-Learning algorithm for difficulty selection
- **ThompsonSamplingAgent**: Bayesian approach for exploration-exploitation
- **AdaptiveQuizManager**: Orchestrates difficulty adaptation
- Reward calculation
- Performance trend analysis

#### 6. **Hybrid Chunker** (`chunking.py`)
- Page-aware chunking
- Semantic splitting
- Metadata preservation (pages, filenames)
- Detailed logging

### Frontend Components

#### 1. **API Client** (`api_client.py`)
- HTTP client for backend communication
- Request/response handling
- Error management
- Methods for all endpoints (upload, chat, quiz, competitive quiz, etc.)

#### 2. **Streamlit Pages**
- **Upload Page**: PDF upload interface with document persistence option
- **Chat Page**: Interactive Q&A with filename display
- **Quiz Page**: Quiz generation and taking with detailed analytics
- **Competitive Quiz Page**: Adaptive quiz with real-time difficulty adjustment
- **Flashcards Page**: Flashcard study interface
- **Summary Page**: Summary generation and display

### Data Flow

```
PDF Document(s)
    │
    ▼
Extracted Text (with filenames)
    │
    ▼
Chunks (with metadata: pages, filenames, indices)
    │
    ▼
Embeddings (1536 dimensions, OpenAI)
    │
    ▼
Pinecone Vector Store
    ├─► Namespace: document_id (UUID)
    ├─► Metadata: filename, page_number, chunk_index
    └─► Vector: 1536-dimensional embedding
    │
    ▼
Retrieval (semantic search with namespace filter)
    │
    ▼
Context for LLM (filtered, sorted, token-managed)
    │
    ▼
Generated Content (answers, quizzes, etc.)
```

---

## 🎓 Adaptive Learning System

### Q-Learning Algorithm

**Purpose**: Learn optimal difficulty selection based on user performance.

**Key Components**:
- **Q-Table**: Maps (current_difficulty, performance_trend) → (next_difficulty) → Q-value
- **Learning Rate (α)**: 0.1 (how quickly to update Q-values)
- **Discount Factor (γ)**: 0.9 (importance of future rewards)
- **Exploration Rate (ε)**: 0.2 (probability of random exploration)

**Update Rule**:
```
Q(state, action) = Q(state, action) + α * [reward + γ * max(Q(next_state)) - Q(state, action)]
```

**States**:
- Current difficulty: low, medium, hard
- Performance trend: improving, stable, declining

**Actions**:
- Next difficulty: low, medium, hard

**Rewards**:
- Correct answer: +0.50 (low), +0.75 (medium), +1.00 (hard)
- Incorrect answer: -0.50 (low), -0.55 (medium), -0.75 (hard)

### Thompson Sampling Algorithm

**Purpose**: Balance exploration (trying different difficulties) and exploitation (using learned optimal difficulty).

**Key Components**:
- **Beta Distribution**: Models success probability for each difficulty level
- **Parameters**: α (successes) and β (failures) for each difficulty
- **Sampling**: Draws from beta distributions to select next difficulty

**Update Rule**:
- Correct answer: α += 1
- Incorrect answer: β += 1

**Selection**:
- Sample from beta distributions for each difficulty
- Select difficulty with highest sampled value

### Adaptive Quiz Manager

**Purpose**: Orchestrates difficulty adaptation using both algorithms.

**Process**:
1. **Calculate Performance Trend**:
   - Analyze last 3-5 answers
   - Determine if performance is improving, stable, or declining

2. **Select Next Difficulty**:
   - Use Q-Learning for exploitation (learned optimal)
   - Use Thompson Sampling for exploration (trying new options)
   - Combine both approaches

3. **Adjust Based on Correctness**:
   - Correct answer → Increase difficulty
   - Incorrect answer → Decrease difficulty
   - Ensure smooth transitions (low → medium → hard)

4. **Calculate Rewards**:
   - Based on correctness and difficulty level
   - Positive for correct, negative for incorrect
   - Higher rewards for harder questions answered correctly

---

## 📊 Key Features Summary

| Feature | Description | Technology Used |
|---------|-------------|-----------------|
| **PDF Upload** | Upload and process multiple PDFs up to 300 pages total | PyMuPDF, FastAPI |
| **Document Indexing** | Extract, chunk, and store in vector DB with namespace isolation | LlamaIndex, Pinecone, OpenAI Embeddings |
| **RAG Chat** | Ask questions with systematic prompting and intelligent fallback | LlamaIndex, OpenAI GPT-4, Pinecone |
| **Quiz Generation** | Generate contextual quizzes with hints | OpenAI GPT-4, LlamaIndex |
| **Quiz Evaluation** | Auto-score MCQ, LLM-evaluate short answers | OpenAI GPT-4 |
| **Performance Analytics** | Visual charts and detailed statistics | Matplotlib, Pandas |
| **Competitive Quiz** | Adaptive difficulty using Q-Learning and Thompson Sampling | NumPy, Custom Algorithms |
| **Flashcards** | Generate and study flashcards | OpenAI GPT-4 |
| **Summaries** | Generate summaries of varying lengths | OpenAI GPT-4, LlamaIndex |
| **Document Persistence** | Continue with existing documents | Pinecone Namespaces |

---

## 🎯 Key Highlights

1. **Contextual Questions**: All quiz questions include sufficient context to be self-contained
2. **Smart Hints**: Hints guide users toward answers without revealing them
3. **AI Evaluation**: Short answers are evaluated using LLM for semantic understanding
4. **Comprehensive Analytics**: Detailed performance reports with visualizations
5. **Adaptive Learning**: Q-Learning and Thompson Sampling for personalized difficulty
6. **Systematic Prompting**: Question-type detection and dynamic prompt generation
7. **Context Management**: Token limit handling, quality filtering, relevance ranking
8. **User-Friendly Interface**: Clean, intuitive Streamlit UI with color-coded feedback
9. **Document Isolation**: Each document is isolated using namespaces in Pinecone
10. **Multiple File Support**: Upload and process multiple PDFs in a single session
11. **Document Persistence**: Continue with existing documents to save API credits
12. **Filename Display**: Actual filenames shown throughout the UI and in responses
13. **Real-time Logging**: Detailed logging of chunking and indexing processes

---

## 🔐 Configuration

The application uses environment variables for configuration:

### Backend (`.env`)
- `OPENAI_API_KEY`: OpenAI API key
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_ENVIRONMENT`: Pinecone environment/region
- `PINECONE_INDEX_NAME`: Name of the Pinecone index
- `BACKEND_HOST`: Backend host (default: 0.0.0.0)
- `BACKEND_PORT`: Backend port (default: 8000)
- `EMBEDDING_MODEL`: Embedding model (default: text-embedding-3-small)
- `LLM_MODEL`: LLM model (default: gpt-4-turbo-preview)
- `LOG_LEVEL`: Logging level (default: INFO)

### Frontend (`.env`)
- `BACKEND_API_URL`: Backend API URL (default: http://localhost:8000)

---

## 🚀 Getting Started

1. **Setup Environment**: Configure `.env` files in both backend and frontend
2. **Install Dependencies**: Install required Python packages
3. **Start Backend**: Run FastAPI server on port 8000
4. **Start Frontend**: Run Streamlit app on port 8501
5. **Upload PDF(s)**: Navigate to upload page and upload PDF(s)
6. **Start Learning**: Use chat, quiz, competitive quiz, flashcards, or summary features

---

## 📝 Notes

- The system automatically creates Pinecone index if it doesn't exist
- All documents are chunked with page boundaries preserved
- Quiz questions are generated with contextual information
- Short answer evaluation uses semantic comparison, not exact matching
- Performance reports include visual charts and detailed insights
- Competitive quiz uses reinforcement learning for adaptive difficulty
- Document sessions are isolated using Pinecone namespaces
- Multiple PDFs are combined with separators and indexed together
- Filenames are preserved and displayed throughout the application

---

*Last Updated: 2024*
