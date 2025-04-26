# Upskillr

Upskillr is an AI-powered career development platform that helps users identify skill gaps and receive personalized recommendations by analyzing their resumes against current job market demands.

## Features

- **Resume Analysis**: Extract education, skills, and experience from PDF resumes using LLMs
- **Skills Gap Detection**: Identify missing skills based on career goals and desired job positions
- **Personalized Recommendations**: Get tailored skill suggestions to enhance your employability
- **RAG-Based Job Matching**: Retrieve relevant job postings using semantic search
- **PDF Resume Parsing**: Clean and extract structured information from resume PDFs

## Prerequisites

- PyMuPDF
- SentenceTransformers
- ChromaDB
- Llama.cpp server or compatible LLM API

## Installation

1. Clone the repository:
```bash
git clone https://github.com/hardikprakash/upskillr.git
cd upskillr
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit the .env file with your configurations
```

The .env file should look like this:
```
API_URL="http://localhost:8080/v1/chat/completions"
MODEL_NAME="Dolphin3.0-Llama3.1-8B-GGUF"
```
Note: The API_KEY variable is optional and can be added if your LLM service requires authentication.

## 🚦 Usage

1. Place your resume PDF in the `data` folder

2. Run the main application:
```bash
cd app
python app.py
```

3. The application will:
   - Parse your resume to extract information
   - Match your profile against relevant job postings
   - Generate personalized skill recommendations

## 🗄️ Project Structure

```
upskillr/
├── app/
│   ├── app.py                          # Main application entry point
│   ├── prompts.py                      # LLM prompt templates
│   ├── resume_parser/                  # Resume parsing components
│   │   ├── pdf_parsing.py              # PDF text extraction and cleaning
│   │   └── detail_extraction.py        # LLM-based information extraction
│   └── rag_components/                 # RAG system for job matching
│       ├── init_db.py                  # ChromaDB initialization
│       ├── retriever.py                # Semantic search for job retrieval
│       └── generator.py                # LLM recommendation generation
├── database/                           # ChromaDB storage
│   └── chroma.sqlite3                  # Vector database for job embeddings
└── data/                               # Directory for resume PDFs
```

## 🧠 How It Works

1. **Resume Parsing Pipeline**:
   - Converts PDF to text using PyMuPDF
   - Cleans and normalizes the text content
   - Uses LLMs to extract structured information (education, skills, experience)

2. **Job Retrieval System**:
   - Stores job postings in a ChromaDB vector database
   - Embeds queries using SentenceTransformers
   - Retrieves semantically similar job postings

3. **Skill Recommendation Engine**:
   - Analyzes user skills against job requirements
   - Identifies skill gaps based on education and experience
   - Generates personalized skill recommendations through LLM prompting

## 📚 API Reference

The project uses a local LLM server or compatible API with the following endpoints:

- POST /v1/chat/completions - For extracting resume information and generating recommendations