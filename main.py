from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from cover_letter_generator import CoverLetterGenerator
from database import DocumentDB
from file_manager import FileManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize our classes
db = DocumentDB()
file_mgr = FileManager()
generator = CoverLetterGenerator()

# Document Management Routes
@app.route('/api/documents/<doc_type>', methods=['GET'])
def list_documents(doc_type):
    """List all documents of a specific type."""
    documents = db.list_documents(doc_type)
    return jsonify(documents)

@app.route('/api/documents/<doc_type>/<name>', methods=['GET'])
def get_document(doc_type, name):
    """Get a specific document by type and name."""
    document = db.get_document(doc_type, name)
    if document:
        return jsonify(document)
    return jsonify({"error": "Document not found"}), 404

@app.route('/api/documents/<doc_type>', methods=['POST'])
def create_document(doc_type):
    """Create a new document."""
    data = request.get_json()
    name = data.get('name')
    content = data.get('content')
    metadata = data.get('metadata', {})
    
    if not name or not content:
        return jsonify({"error": "Name and content are required"}), 400
    
    success = db.save_document(doc_type, name, content, metadata)
    if success:
        file_mgr.write_file(doc_type, name, content)
        return jsonify({"success": True})
    return jsonify({"error": "Failed to save document"}), 500

@app.route('/api/documents/<doc_type>/<name>', methods=['DELETE'])
def delete_document(doc_type, name):
    """Delete a document."""
    success = db.delete_document(doc_type, name)
    if success:
        file_mgr.delete_file(doc_type, name)
        return jsonify({"success": True})
    return jsonify({"error": "Failed to delete document"}), 500

# Biography Routes
@app.route('/api/biography', methods=['GET'])
def get_biography():
    """Get the current biography."""
    biography = db.get_biography()
    if biography:
        return jsonify(biography)
    return jsonify({"error": "No biography found"}), 404

@app.route('/api/biography', methods=['POST'])
def update_biography():
    """Update the biography."""
    data = request.get_json()
    content = data.get('content')
    notes = data.get('notes', '')
    
    if not content:
        return jsonify({"error": "Content is required"}), 400
    
    success = db.save_biography(content, notes)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Failed to save biography"}), 500

@app.route('/api/biography/versions', methods=['GET'])
def list_biography_versions():
    """List all biography versions."""
    versions = db.list_biography_versions()
    return jsonify(versions)

@app.route('/api/biography/<int:version>', methods=['GET'])
def get_biography_version(version):
    """Get a specific biography version."""
    biography = db.get_biography(version)
    if biography:
        return jsonify(biography)
    return jsonify({"error": "Version not found"}), 404

# Cover Letter Generation Routes
@app.route('/api/generate-cover-letter', methods=['POST'])
def generate_cover_letter():
    """Generate a cover letter."""
    data = request.get_json()
    print("\n=== Starting Cover Letter Generation ===")
    print("Request Data:", data)
    
    resume_name = data.get('resume_name')
    job_desc_name = data.get('job_description_name')
    sample_letter_name = data.get('sample_letter_name')
    preferences = data.get('preferences', '')
    
    # Get documents from database
    resume = db.get_document('resume', resume_name)
    job_desc = db.get_document('job_description', job_desc_name)
    sample_letter = db.get_document('cover_letter', sample_letter_name)
    
    print("\nDocument Retrieval:")
    print(f"Resume found: {bool(resume)}")
    print(f"Job Description found: {bool(job_desc)}")
    print(f"Sample Letter found: {bool(sample_letter)}")
    
    if not all([resume, job_desc, sample_letter]):
        error_msg = "Missing required documents"
        print(f"\nError: {error_msg}")
        return jsonify({"error": error_msg}), 400
    
    try:
        print("\nProcessing user information...")
        # Process user information
        user_profile = generator.process_user_info(
            resume['content'],
            [sample_letter['content']],
            preferences
        )
        print("User profile generated successfully")
        
        print("\nAnalyzing job...")
        # Analyze job
        job_analysis = generator.analyze_job(job_desc['content'])
        print("Job analysis completed successfully")
        
        print("\nAligning profile with job...")
        # Match profile with job
        alignment = generator.align_profile_with_job(user_profile, job_analysis)
        print("Profile-job alignment completed successfully")
        
        print("\nGenerating cover letter...")
        # Generate cover letter
        cover_letter = generator.generate_cover_letter(alignment, sample_letter['content'])
        print("Cover letter generated successfully")
        
        result = {
            "cover_letter": cover_letter,
            "user_profile": user_profile,
            "job_analysis": job_analysis,
            "alignment": alignment
        }
        print("\n=== Generation Complete ===")
        return jsonify(result)
    
    except Exception as e:
        error_msg = str(e)
        print(f"\nError during generation: {error_msg}")
        print("Full error:", e)
        return jsonify({"error": error_msg}), 500

# AI Prompt Routes
@app.route('/api/prompts', methods=['GET'])
def list_prompts():
    """List all AI prompts."""
    prompts = db.list_prompts()
    return jsonify(prompts)

@app.route('/api/prompts/<name>', methods=['GET'])
def get_prompt(name):
    """Get a specific AI prompt."""
    prompt = db.get_prompt(name)
    if prompt:
        return jsonify(prompt)
    return jsonify({"error": "Prompt not found"}), 404

@app.route('/api/prompts/<name>', methods=['POST'])
def save_prompt(name):
    """Save or update an AI prompt."""
    data = request.get_json()
    content = data.get('content')
    description = data.get('description', '')
    
    if not content:
        return jsonify({"error": "Content is required"}), 400
    
    success = db.save_prompt(name, content, description)
    if success:
        return jsonify({"success": True})
    return jsonify({"error": "Failed to save prompt"}), 500

if __name__ == '__main__':
    # Initialize database with default prompts if they don't exist
    if not db.list_prompts():
        db.initialize_default_prompts()
    app.run(host='127.0.0.1', port=5000, debug=True) 