# Cover Letter Generator

## Overview

A powerful command-line application that leverages OpenAI's GPT models to generate personalized, professional cover letters. The application analyzes your resume, job descriptions, and preferences to create tailored cover letters that highlight your most relevant qualifications.

## Features

### Core Functionality
- **Smart Resume Analysis**: Extracts key qualifications and achievements from your resume
- **Job Description Analysis**: Identifies core requirements and preferred qualifications
- **Profile Alignment**: Matches your experience with job requirements
- **Custom Cover Letter Generation**: Creates tailored cover letters using your preferred style
- **Biography Management**: Maintains a version-controlled professional biography

### Document Management
- Import documents from various formats (PDF, TXT, MD, JSON, YAML, HTML)
- Local SQLite database for efficient document storage and retrieval
- Version control for biographical information
- File-based backup system

### User Interface
- Interactive command-line interface with rich text formatting
- Clear menu-driven navigation
- Real-time progress feedback
- Markdown-formatted output

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- SQLite 3 (typically included with Python)
- OpenAI API key

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/cover-letter-generator.git
   cd cover-letter-generator
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Quick Start

1. **Launch the Application**
   ```bash
   python cover_letter_generator.py
   ```

2. **Import Your Documents**
   - Add your resume (PDF or text format)
   - Import sample cover letters for style reference
   - Add job descriptions

3. **Generate a Cover Letter**
   - Select your resume
   - Choose a job description
   - Pick a sample letter for style
   - Add any specific preferences
   - Generate and save your personalized cover letter

## Project Structure

```
cover-letter-generator/
├── cover_letter_generator.py  # Main application logic
├── database.py               # SQLite database management
├── file_manager.py          # File I/O operations
├── requirements.txt         # Project dependencies
├── .env                    # Environment variables
└── documents/              # Document storage
    ├── resumes/
    ├── cover_letters/
    ├── job_descriptions/
    └── biography/
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Verify your API key in the `.env` file
   - Check if the API key has sufficient credits
   - Ensure the `.env` file is in the project root

2. **PDF Import Issues**
   - Confirm the PDF is not password-protected
   - Check if the PDF contains extractable text
   - Try converting to text format if extraction fails

3. **Database Errors**
   - Ensure SQLite is properly installed
   - Check write permissions in the project directory
   - Verify database file integrity

## Contributing

Contributions are welcome! Here's how you can help:

1. **Report Issues**
   - Use the issue tracker to report bugs
   - Include detailed steps to reproduce the issue
   - Attach relevant error messages

2. **Submit Pull Requests**
   - Fork the repository
   - Create a feature branch
   - Follow the existing code style
   - Add tests for new features
   - Update documentation

3. **Improve Documentation**
   - Fix typos or unclear instructions
   - Add examples and use cases
   - Translate documentation

## License

This project is open-source and available under the MIT License. See the LICENSE file for more details.

## Acknowledgments

- OpenAI for providing the GPT API
- Rich library for terminal formatting
- PyPDF2 for PDF processing
- All contributors and users of this project

---

For additional support or questions, please open an issue on the project repository.
