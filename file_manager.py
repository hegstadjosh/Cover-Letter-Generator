import os
from typing import Optional, Dict, Tuple
from pathlib import Path
from PyPDF2 import PdfReader
import re

class FileManager:
    def __init__(self, base_dir: str = "documents"):
        """Initialize file manager with base directory for document storage."""
        self.base_dir = Path(base_dir)
        self._create_directories()

    def _create_directories(self):
        """Create necessary directories if they don't exist."""
        for dir_name in ["resumes", "cover_letters", "job_descriptions", "biography", "prompts"]:
            (self.base_dir / dir_name).mkdir(parents=True, exist_ok=True)

    def _read_pdf(self, file_path: str) -> Optional[str]:
        """Read content from a PDF file."""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Clean up the text
            text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
            text = re.sub(r'\n\s*\n', '\n\n', text)  # Replace multiple newlines with double newline
            text = text.strip()
            
            return text
        except Exception as e:
            print(f"Error reading PDF file: {e}")
            return None

    def read_file(self, file_path: str) -> Optional[str]:
        """Read content from a file."""
        try:
            # Check if it's a PDF file
            if file_path.lower().endswith('.pdf'):
                return self._read_pdf(file_path)
            
            # For text files
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # If UTF-8 fails, try other common encodings
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                print(f"Error reading file with latin-1 encoding: {e}")
                return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def write_file(self, doc_type: str, name: str, content: str) -> Optional[str]:
        """Write content to a file in the appropriate directory."""
        try:
            # Determine the directory based on document type
            if doc_type == "resume":
                dir_path = self.base_dir / "resumes"
            elif doc_type == "cover_letter":
                dir_path = self.base_dir / "cover_letters"
            elif doc_type == "job_description":
                dir_path = self.base_dir / "job_descriptions"
            elif doc_type == "biography":
                dir_path = self.base_dir / "biography"
            else:
                print(f"Invalid document type: {doc_type}")
                return None
            
            # Create a valid filename
            filename = f"{name}.txt"
            file_path = dir_path / filename
            
            # Write the content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return str(file_path)
        except Exception as e:
            print(f"Error writing file: {e}")
            return None

    def import_file(self, file_path: str) -> Optional[str]:
        """Import a file and return its contents."""
        # Clean up the path - remove quotes and normalize path separators
        file_path = file_path.strip('"\'').strip()
        file_path = os.path.normpath(file_path)
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            # Try with raw string interpretation
            raw_path = repr(file_path)[1:-1]  # Remove the quotes from repr
            if os.path.exists(raw_path):
                file_path = raw_path
            else:
                return None
        
        return self.read_file(file_path)

    def get_file_info(self, file_path: str) -> Tuple[bool, str, str]:
        """Get information about a file: (is_valid, file_type, error_message)."""
        # Clean up the path - remove quotes and normalize path separators
        file_path = file_path.strip('"\'').strip()
        file_path = os.path.normpath(file_path)
        
        if not os.path.exists(file_path):
            # Try with raw string interpretation
            raw_path = repr(file_path)[1:-1]  # Remove the quotes from repr
            if os.path.exists(raw_path):
                file_path = raw_path
            else:
                return False, "", "File not found"
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Check supported file types
        if file_ext == '.pdf':
            return True, "pdf", ""
        elif file_ext in ['.txt', '.md', '.json', '.yaml', '.html']:
            return True, "text", ""
        else:
            return False, "", f"Unsupported file type: {file_ext}"

    def export_file(self, content: str, file_path: str) -> bool:
        """Export content to a specified file path."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error exporting file: {e}")
            return False

    def list_files(self, doc_type: str) -> list:
        """List all files in a specific document directory."""
        try:
            dir_path = self.base_dir / doc_type
            if not dir_path.exists():
                return []
            
            return [f.name for f in dir_path.iterdir() if f.is_file()]
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def delete_file(self, doc_type: str, name: str) -> bool:
        """Delete a file from the appropriate directory."""
        try:
            for ext in ['.txt', '.json', '.html', '.yaml']:
                file_path = self.base_dir / doc_type / f"{name}{ext}"
                if file_path.exists():
                    file_path.unlink()
                    return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False 