# Upskillr

Upskillr is an AI-powered career development app that helps users identify skill gaps and receive personalized recommendations by analyzing their resumes against current job market demands.

**Hosted at**: https://upskillr.streamlit.app

## Features

- **Resume Analysis**: Extract education, skills, and experience from PDF resumes using LLMs
- **Skills Gap Detection**: Identify missing skills based on career goals and desired job positions
- **Personalized Recommendations**: Get tailored skill suggestions to enhance your employability
- **RAG-Based Job Matching**: Retrieve relevant job postings using semantic search
- **PDF Resume Parsing**: Clean and extract structured information from resume PDFs

## Prerequisites

- Python 3.8+
- OpenRouter API Key (get from https://openrouter.ai/keys)
- PyMuPDF
- SentenceTransformers
- ChromaDB

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
# Edit the .env file with your OpenRouter API key and configurations
```

The .env file should look like this:
```
OPENROUTER_API_KEY="your_openrouter_api_key_here"
API_URL="https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME="openai/gpt-oss-20b:free"
FALLBACK_MODEL_NAME="deepseek/deepseek-r1t-chimera:free"
APP_URL="https://github.com/hardikprakash/upskillr"
APP_NAME="Upskillr"
```

## Getting Your OpenRouter API Key

1. Visit https://openrouter.ai/
2. Sign up for a free account
3. Navigate to https://openrouter.ai/keys
4. Create a new API key
5. Copy the key and add it to your `.env` file

## Usage

1. Ensure you have your OpenRouter API key configured in `.env`

2. Run the Streamlit application:
```bash
streamlit run app/app.py
```

3. The application will:
   - Parse your resume to extract information
   - Match your profile against relevant job postings
   - Generate personalized skill recommendations

## Project Structure

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

## How It Works

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
   - Generates personalized skill recommendations through OpenRouter LLMs

## Technology Stack

- **Frontend**: Streamlit
- **LLM Provider**: OpenRouter API
  - Primary Model: `openai/gpt-oss-20b:free`
  - Fallback Model: `deepseek/deepseek-r1t-chimera:free`
- **Vector Database**: ChromaDB
- **Embeddings**: SentenceTransformers (all-MiniLM-L6-v2)
- **PDF Processing**: PyMuPDF
- **HTTP Client**: Requests
