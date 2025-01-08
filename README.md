# Cover Letter Generator

An AI-powered cover letter generator built with React, Flask, and OpenAI's GPT models. This application helps you create personalized cover letters by analyzing your resume, job descriptions, and previous cover letters.

## Features

-�� AI-powered cover letter generation using OpenAI's GPT models
- 📄 Upload and manage resumes in various formats
- 💼 Store and organize job descriptions
- ✍️ Generate tailored cover letters using AI
- 👤 Maintain a professional biography with version history
- ⚙️ Customize AI prompts for different aspects of the generation process
- 🎨 Modern, responsive UI built with Material-UI
- 🔄 Version history for your professional biography
- 📱 Mobile-friendly interface

## Tech Stack

- **Frontend**: React, TypeScript, Material-UI
- **Backend**: Python, Flask
- **Database**: SQLite
- **AI**: OpenAI GPT API
- **File Processing**: PyPDF2

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- OpenAI API key
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cover-letter-generator
   ```

2. Set up the backend:
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\activate
   
   # On Unix or MacOS:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

1. Start the backend server (in the root directory):
   ```bash
   # Ensure virtual environment is activated
   python main.py
   ```
   The backend server will run on http://localhost:5000

2. Start the frontend development server (in the frontend directory):
   ```bash
   npm start
   ```
   The frontend will run on http://localhost:3000

## Project Structure

```
cover-letter-generator/
├── backend/
│   ├── cover_letter_generator.py  # Core generation logic
│   ├── database.py               # Database operations
│   ├── file_manager.py          # File handling
│   ├── main.py                  # Flask application
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── public/                  # Static assets
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   └── utils/             # Utility functions
│   ├── package.json           # Node dependencies
│   └── tsconfig.json         # TypeScript config
├── .env.example              # Example environment variables
├── .gitignore               # Git ignore rules
├── LICENSE                  # MIT license
└── README.md               # Project documentation
```

## Usage Guide

1. **Initial Setup**:
   - Add your OpenAI API key to the `.env` file
   - Start both backend and frontend servers

2. **Resume Management**:
   - Upload your resume(s) in PDF or DOCX format
   - The system will parse and store your resume information

3. **Job Description Management**:
   - Add job descriptions you're applying for
   - Tag and categorize job postings

4. **Cover Letter Generation**:
   - Select your resume and job description
   - Choose a writing style
   - Add custom instructions if needed
   - Generate and edit the cover letter
   - Export to your preferred format

5. **Biography Management**:
   - Maintain your professional biography
   - Track changes with version history
   - Use it as additional context for generation

## API Documentation

### Documents API
- `GET /api/documents/<doc_type>` - List all documents
- `POST /api/documents/<doc_type>` - Upload new document
- `GET /api/documents/<doc_type>/<id>` - Get specific document
- `DELETE /api/documents/<doc_type>/<id>` - Delete document

### Generation API
- `POST /api/generate-cover-letter` - Generate cover letter
- `GET /api/prompts` - Get generation prompts
- `POST /api/prompts` - Update prompts

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

- **Backend won't start**: Check Python version and virtual environment activation
- **Frontend build fails**: Ensure Node.js version is compatible and dependencies are installed
- **Generation errors**: Verify OpenAI API key and rate limits
- **File upload issues**: Check file permissions and supported formats

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for the GPT API
- Material-UI for the component library
- All contributors who have helped improve this project
