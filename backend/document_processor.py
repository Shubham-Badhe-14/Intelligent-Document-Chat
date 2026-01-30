from pypdf import PdfReader
from io import BytesIO

def extract_text(file_content: bytes, filename: str) -> str:
    """Extracts text from PDF or Text file content."""
    if filename.lower().endswith(".pdf"):
        return _extract_from_pdf(file_content)
    else:
        # Assume text file
        return file_content.decode("utf-8", errors="ignore")

def _extract_from_pdf(file_content: bytes) -> str:
    """Extracts text from a PDF file."""
    reader = PdfReader(BytesIO(file_content))
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Splits text into overlapping chunks of approximately `chunk_size` words."""
    words = text.split()
    chunks = []
    
    if not words:
        return []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        
        # Break if we've reached the end
        if i + chunk_size >= len(words):
            break
            
    return chunks
