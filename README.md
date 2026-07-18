# DocsInsight AI: Full-Stack PDF Q&A Assistant

A production-ready, full-stack Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents and chat with them using the power of Google's Gemini AI.

## 🚀 Features
- **Secure Authentication:** User registration and login powered by JWT (JSON Web Tokens) and bcrypt hashing.
- **Document Management:** Upload PDFs, parse them, and securely store them in a local SQLite database and ChromaDB vector store.
- **Advanced AI Pipeline:** Built with LangChain, utilizing Google's `gemini-1.5-flash` for blazing-fast responses and `gemini-embedding-001` for high-quality semantic search.
- **Interactive UI:** A beautiful, responsive chat interface built with Streamlit.
- **Session History:** Continuous chat history logging across sessions.

## 🛠️ Tech Stack
- **Frontend:** Streamlit
- **Backend:** FastAPI, Uvicorn, SQLAlchemy (SQLite)
- **AI & RAG:** LangChain, ChromaDB, Google Generative AI (Gemini)
- **Environment:** Unified Python Virtual Environment (`venv`)

## 📦 Installation & Setup

1. **Clone the repository:**
   ```powershell
   git clone https://github.com/RajGajera03/DocsInsight-AI.git
   cd DocsInsight-AI
   ```

2. **Set up the virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Navigate to the `backend` folder and create a `.env` file (or update the existing one):
   ```env
   # backend/.env
   DATABASE_URL=sqlite:///./pdf_qa.db
   SECRET_KEY=your_super_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   GOOGLE_API_KEY="AIzaSy_YOUR_GEMINI_API_KEY_HERE"
   ```
   *(Note: You must get a valid Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey))*

## 🏃‍♂️ Running the Application

For your convenience, Windows startup scripts are included in the root directory!

1. **Start the Backend:**
   Simply double-click `run_backend.bat` in your file explorer or run:
   ```powershell
   .\run_backend.bat
   ```
   *The FastAPI server will start at `http://127.0.0.1:8000`*

2. **Start the Frontend:**
   Simply double-click `run_frontend.bat` in your file explorer or run:
   ```powershell
   .\run_frontend.bat
   ```
   *The Streamlit UI will open in your browser automatically.*

## 🐳 Docker Deployment (Optional)
If you prefer running the application in isolated containers, a `docker-compose.yml` file is provided:
```powershell
docker-compose up --build
```
