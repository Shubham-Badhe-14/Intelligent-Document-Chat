# Intelligent Document Chat

![AI Document Chatbot](docs/images/app_screenshot.png)

A powerful **Retrieval-Augmented Generation (RAG)** chatbot that allows users to upload PDF documents and interact with them using natural language. Built with a modern, responsive UI and powered by Google's Gemini Pro model, this tool makes document analysis intuitive and efficient.

## 🚀 Features

-   **📄 Smart Document Processing**: Upload PDF or text files and instantly extract insights.
-   **💬 Context-Aware Chat**: Ask questions and get answers based strictly on the document content using RAG technology.
-   **👁️ PDF Preview**: View the uploaded PDF side-by-side with the chat interface for easy reference.
-   **✨ specialized Prompts**: One-click actions for:
    -   **Summarization**: Get a quick overview of the document.
    -   **Specific Details**: Extract key facts and figures.
    -   **Creative Writing**: Generate creative content based on the text.
-   **📚 Citation Support**: Answers include citations to the specific sources used, ensuring accuracy.

## 🛠️ Tech Stack

### Backend
-   **Python 3.10+**
-   **FastAPI**: High-performance web framework for building APIs.
-   **Google Gemini API**: State-of-the-art LLM for text generation.
-   **FAISS**: Efficient similarity search and clustering of dense vectors.
-   **PyPDF**: Robust PDF parsing and text extraction.

### Frontend
-   **HTML5 & CSS3**: Modern, semantic markup and styling.
-   **React**: Dynamic UI built with functional components.
-   **Babel Standalone**: In-browser JSX compilation for a build-free setup.

## 📋 Prerequisites

Before you begin, ensure you have:
1.  **Python 3.10** or higher installed.
2.  A **Google Gemini API Key**. You can get one [here](https://makersuite.google.com/app/apikey).

## ⚡ Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ai_document_chatbot
```

### 2. Backend Setup
Navigate to the `backend` directory and install the required dependencies:

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and add your API key:

```bash
# backend/.env
GEMINI_API_KEY=your_api_key_here
```

Start the backend server:

```bash
python main.py
```
The API will be available at `http://localhost:8000`.

### 3. Frontend Setup
Open a new terminal window and navigate to the `frontend` directory:

```bash
cd frontend
```

Start a simple HTTP server (Python's built-in server is recommended):

```bash
python -m http.server 8080
```

### 4. Running the App
Open your web browser and navigate to:
**[http://localhost:8080](http://localhost:8080)**

## 🎮 Usage Guide

1.  **Upload**: Click the "New Upload" button in the sidebar and select a PDF file.
2.  **Select**: Click on the uploaded file in the "Your Files" list.
3.  **View**: Click "Show PDF" to open the document viewer.
4.  **Chat**: Type your question in the chat bar or use one of the suggested prompts to start analyzing!
