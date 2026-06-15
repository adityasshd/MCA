# 📚 MCA AI Study Suite

An AI-powered desktop learning application built for MCA (Master of Computer Applications) coursework. It uses RAG (Retrieval-Augmented Generation), automated exam generation, and analytics to transform raw PDF textbooks into an interactive study experience.

---

## ✨ Features

- **PDF Processing** — Automatically splits multi-chapter PDFs into individual chapters and extracts embedded images.
- **AI-Powered Study Guides** — Generates chapter summaries and study material using configurable LLM providers (Ollama, Groq, OpenAI, Gemini).
- **RAG-Based Q&A** — Ask questions about your course material and get contextually grounded answers via vector search.
- **Exam Generation** — AI examiner agent creates practice exams with multi-pass question refinement.
- **Analytics Dashboard** — Track study progress with interactive Plotly charts.
- **AI Tutor Chat** — Real-time conversational tutor embedded in the UI.
- **Multi-Backend Storage** — Supports MongoDB Atlas, SQLite, and in-memory backends.
- **Flexible Embeddings** — Local (all-MiniLM-L6-v2), OpenAI, or MongoDB/Voyage AI embeddings.
- **PyQt6 Desktop UI** — Modern dark-themed GUI with custom cards, flow layouts, and WebEngine views.

---

## 📁 Project Structure

```
MCA/
├── main.py                    # Entry point (GUI + CLI)
├── splitter.py                # PDF → chapter splitter
├── extract_all_images.py      # Image extraction from PDFs
├── generate_chapter_content.py# AI-powered chapter content generation
├── verify_chapter_content.py  # Content verification utility
├── pyproject.toml             # Project metadata & dependencies
│
├── src/
│   ├── agents/                # AI agents
│   │   ├── study_agent.py     #   Study guide generator
│   │   └── examiner_agent.py  #   Exam/question generator
│   ├── core/                  # Core infrastructure
│   │   ├── config.py          #   Centralised app configuration
│   │   ├── database.py        #   Database manager (Mongo/SQLite/Memory)
│   │   ├── models.py          #   LLM model manager (multi-provider)
│   │   ├── prompt_manager.py  #   Prompt template loader
│   │   └── schemas.py         #   Pydantic data models
│   ├── prompts/               # LLM prompt templates
│   ├── rag/                   # Retrieval-Augmented Generation
│   │   ├── indexer.py         #   Document chunking & vector indexing
│   │   └── retriever.py       #   Semantic search & retrieval
│   ├── reporting/             # Report generation
│   │   └── report_builder.py
│   └── ui/                    # PyQt6 desktop interface
│       ├── main_window.py     #   Main application window
│       ├── dashboard.py       #   Home dashboard
│       ├── study_view.py      #   Study material viewer
│       ├── test_view.py       #   Exam/test interface
│       ├── analytics_view.py  #   Analytics & charts
│       ├── subject_manager.py #   Subject CRUD
│       ├── settings_dialog.py #   Settings panel
│       ├── theme.py           #   Dark theme styling
│       ├── workers.py         #   Background task workers
│       └── components/        #   Reusable UI components
│           ├── ai_tutor.py    #     AI chat widget
│           ├── custom_card.py #     Card component
│           └── flow_layout.py #     Flow layout manager
│
├── data/
│   ├── raw/                   # Original PDF textbooks
│   └── processed/             # Extracted content
│       ├── chapters/          #   Split chapter PDFs
│       ├── chapter_content/   #   AI-generated markdown content
│       └── images/            #   Extracted images per subject
│
└── Kaggle_Notebook.ipynb      # Remote GPU notebook for heavy inference
```

---

## 🛠️ Setup

### Prerequisites

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** (recommended) or pip
- **MongoDB Atlas** account (or use SQLite/memory backend)
- **Ollama** (for local LLM inference) or API keys for cloud providers

### Installation

```bash
# Clone the repository
git clone https://github.com/adityasshd/MCA.git
cd MCA

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
```

### Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```env
# Database
DB_BACKEND=mongodb          # mongodb | sqlite | memory
MONGODB_USERNAME=your_user
MONGODB_PASSWORD=your_pass
MONGODB_SERVER_URL=your_atlas_url

# LLM Providers (configure at least one)
GROQ_API_KEY=your_key
GEMINI_API_KEY=your_key
OPENAI_API_KEY=your_key

# Model Selection
TIER1_PROVIDER=ollama       # Fast model for summaries
TIER1_MODEL=llama3.2:1b
TIER2_PROVIDER=ollama       # Reasoning model for exams
TIER2_MODEL=qwen2.5:1.5b

# Embeddings
EMBEDDING_PROVIDER=local    # local | openai | mongodb
```

---

## 🚀 Usage

### Launch the GUI

```bash
python main.py
```

### CLI — Split PDFs into Chapters

```bash
python main.py --split                    # Split all books
python main.py --split "BOOK_NAME"        # Split specific book(s)
```

### CLI — Run RAG Indexing

```bash
python main.py --index
```

### Generate Chapter Content (AI Summaries)

```bash
python generate_chapter_content.py
```

---

## 📖 Subjects Covered

| Subject | Code |
|---------|------|
| Fundamentals of Computer and C Programming | ECAP012 |
| Object Oriented Programming Using C++ | ECAP444 |
| Software Engineering Practices | ECAP437 |
| Data Warehousing and Data Mining | ECAP446 |
| Linux and Shell Scripting | ECAP448 |
| Data Communication and Networking | ECAP453 |
| Analytical Skills-I | EPEA515 |

---

## 🧠 Architecture

```
PDF Textbooks ──► Splitter ──► Chapters ──► RAG Indexer ──► Vector DB
                                  │                            │
                                  ▼                            ▼
                          AI Content Gen              Semantic Retrieval
                                  │                            │
                                  ▼                            ▼
                          Study Guides              Study Agent / Tutor
                                                           │
                                                           ▼
                                                   Examiner Agent
                                                           │
                                                           ▼
                                                    PyQt6 Desktop UI
                                                  (Dashboard, Study,
                                                   Tests, Analytics)
```

---

## 📄 License

This project is for personal academic use.
